#!/usr/bin/env python3

#-jc safe EC2 environment cleanup by Name tag

import argparse
import boto3
import sys
import time

DEFAULT_REGION = "us-east-1"
SSM_PREFIX = "/critchley/aws/ec2-keypairs/"


def eprint(msg):
    print(msg, file=sys.stderr)


def find_instance(ec2, name):
    resp = ec2.describe_instances(
        Filters=[{"Name": "tag:Name", "Values": [name]}]
    )

    for r in resp["Reservations"]:
        for i in r["Instances"]:
            return i

    return None


def keypair_exists(ec2, key_name):
    try:
        ec2.describe_key_pairs(KeyNames=[key_name])
        return True
    except ec2.exceptions.ClientError:
        return False


def ssm_param_exists(ssm, name):
    try:
        ssm.get_parameter(Name=name)
        return True
    except ssm.exceptions.ParameterNotFound:
        return False


def countdown(seconds, quiet):
    if not sys.stdin.isatty():
        return
    if quiet:
        return

    print(f"Waiting {seconds} seconds before proceeding (Ctrl-C to abort)...")
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Cleanup EC2 environment safely")
    parser.add_argument("name", help="Instance Name tag")
    parser.add_argument("--yes", action="store_true", help="Skip interactive confirmation")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    ec2 = boto3.client("ec2", region_name=args.region)
    ssm = boto3.client("ssm", region_name=args.region)

    quiet = args.quiet

    inst = find_instance(ec2, args.name)

    if inst:
        state = inst["State"]["Name"]
        instance_id = inst["InstanceId"]
        key_name = inst.get("KeyName")

        if not quiet:
            print(f"Instance found: {instance_id} ({state})")

        if state == "running":
            eprint("Refusing to terminate: instance is running.")
            sys.exit(1)

        if state == "stopping":
            if not quiet:
                print("Instance is stopping. Waiting to reach stopped state...")
            waiter = ec2.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[instance_id])
            inst = find_instance(ec2, args.name)
            state = inst["State"]["Name"]

        if state == "stopped":
            if not args.yes:
                answer = input("Type 'yes' to terminate: ").strip().lower()
                if answer != "yes":
                    print("Aborted.")
                    sys.exit(1)
            else:
                countdown(5, quiet)

            if not quiet:
                print("Terminating instance...")

            ec2.terminate_instances(InstanceIds=[instance_id])
            waiter = ec2.get_waiter("instance_terminated")
            waiter.wait(InstanceIds=[instance_id])

            if not quiet:
                print("Instance terminated.")

        elif state == "terminated":
            if not quiet:
                print("Instance already terminated.")

        else:
            eprint(f"Unexpected instance state: {state}")
            sys.exit(1)

    else:
        if not quiet:
            print("Instance not found.")

        key_name = f"{args.name}"

    # Keypair cleanup
    if key_name:
        if keypair_exists(ec2, key_name):
            if not quiet:
                print(f"Deleting keypair: {key_name}")
            ec2.delete_key_pair(KeyName=key_name)
        else:
            if not quiet:
                print(f"Keypair not found: {key_name}")

    # SSM cleanup
    param_name = SSM_PREFIX + args.name
    if ssm_param_exists(ssm, param_name):
        if not quiet:
            print(f"Deleting SSM parameter: {param_name}")
        ssm.delete_parameter(Name=param_name)
    else:
        if not quiet:
            print(f"SSM parameter not found: {param_name}")

    # Final validation
    inst = find_instance(ec2, args.name)

    instance_alive = False
    if inst:
        state = inst["State"]["Name"]
        if state not in ("terminated",):
            instance_alive = True

    kp_exists = keypair_exists(ec2, key_name) if key_name else False
    ssm_exists = ssm_param_exists(ssm, param_name)

    if instance_alive or kp_exists or ssm_exists:
        eprint("Cleanup incomplete:")
        if instance_alive:
            eprint(f" - Instance still in state: {state}")
        if kp_exists:
            eprint(" - Keypair still exists")
        if ssm_exists:
            eprint(" - SSM parameter still exists")
        sys.exit(1)


    if not quiet:
        print("Cleanup complete.")

    sys.exit(0)


if __name__ == "__main__":
    main()
