#!/usr/bin/env python3
#-jc idempotent EC2 launcher by Name tag with per-host key management

import sys
import time
from pathlib import Path

import boto3

# DEFAULT_AMI = "ami-0b83ef932dab936e6"  # my baseline — change if needed
DEFAULT_AMI = "ami-095f312bef9bfe5b1"  # clean-room test
DEFAULT_TYPE = "t3.medium"
DEFAULT_REGION = "us-east-1"
DEFAULT_KEY_SUFFIX = ""  # e.g. "-key" if you prefer


def usage():
    print("Usage: awslaunch.py <name> [instance_type] [profile]")
    sys.exit(1)


#-jc find existing instance by Name tag (non-terminated)
def find_instance_by_name(ec2, name):
    resp = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": [name]},
            {
                "Name": "instance-state-name",
                "Values": ["pending", "running", "stopping", "stopped"],
            },
        ]
    )

    for r in resp["Reservations"]:
        for i in r["Instances"]:
            return i
    return None


#-jc ensure keypair consistency (idempotent and safe)
def ensure_keypair(ec2, key_name: str, pem_path: Path) -> Path:
    local_exists = pem_path.exists()

    try:
        ec2.describe_key_pairs(KeyNames=[key_name])
        aws_exists = True
    except ec2.exceptions.ClientError:
        aws_exists = False

    # Case C — AWS has key but local private key missing
    if aws_exists and not local_exists:
        raise SystemExit(
            f"ERROR: keypair '{key_name}' exists in AWS but "
            f"{pem_path} is missing locally. Cannot recover private key."
        )

    # Case A — need to create keypair
    if not aws_exists:
        kp = ec2.create_key_pair(KeyName=key_name)
        pem_path.parent.mkdir(parents=True, exist_ok=True)
        pem_path.write_text(kp["KeyMaterial"])
        pem_path.chmod(0o600)

    # Case B — both exist → reuse
    if local_exists:
        pem_path.chmod(0o600)

    return pem_path


def get_public_ip(ec2, instance_id):
    desc = ec2.describe_instances(InstanceIds=[instance_id])
    inst = desc["Reservations"][0]["Instances"][0]
    return inst.get("PublicIpAddress"), inst["State"]["Name"]


def main():
    if len(sys.argv) < 2:
        usage()

    name = sys.argv[1]
    instance_type = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_TYPE
    profile = sys.argv[3] if len(sys.argv) >= 4 else None

    #-jc session
    if profile:
        session = boto3.Session(profile_name=profile)
        ec2 = session.client("ec2", region_name=DEFAULT_REGION)
    else:
        ec2 = boto3.client("ec2", region_name=DEFAULT_REGION)

    key_name = f"{name}{DEFAULT_KEY_SUFFIX}"
    pem_path = Path.home() / ".ssh" / f"{key_name}.pem"

    #-jc ensure key state is sane before anything else
    ensure_keypair(ec2, key_name, pem_path)

    #-jc check for existing instance
    existing = find_instance_by_name(ec2, name)

    if existing:
        instance_id = existing["InstanceId"]
        print(f"Instance already exists: {instance_id}")

        # ensure running
        state = existing["State"]["Name"]
        if state == "stopped":
            print("Starting stopped instance…")
            ec2.start_instances(InstanceIds=[instance_id])
            waiter = ec2.get_waiter("instance_running")
            waiter.wait(InstanceIds=[instance_id])

        # fetch IP (may need to wait)
        ip, state = get_public_ip(ec2, instance_id)

        if not ip:
            print("Waiting for public IP…")
            waiter = ec2.get_waiter("instance_running")
            waiter.wait(InstanceIds=[instance_id])
            time.sleep(2)
            ip, _ = get_public_ip(ec2, instance_id)

        print("Instance:", instance_id)
        print("Public IP:", ip)
        print("Changed: false")
        return

    #-jc create new instance
    print(f"Launching {instance_type} named '{name}'…")

    resp = ec2.run_instances(
        ImageId=DEFAULT_AMI,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": name}],
            }
        ],
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "VolumeSize": 16,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": True,
                },
            }
        ],
    )

    instance_id = resp["Instances"][0]["InstanceId"]
    print("Instance:", instance_id)

    print("Waiting for running state…")
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])

    # small settle delay
    time.sleep(2)

    ip, _ = get_public_ip(ec2, instance_id)

    print("Public IP:", ip)
    print("Changed: true")


if __name__ == "__main__":
    main()
