#!/usr/bin/env python3

#-jc terminate EC2 instance by Name tag with safety checks

import argparse
import boto3
import os
import sys
import time
import select
from pathlib import Path
import termios
import tty

DEFAULT_REGION = "us-east-1"


def find_instance(ec2, name):
    resp = ec2.describe_instances(
        Filters=[{"Name": "tag:Name", "Values": [name]}]
    )

    for r in resp["Reservations"]:
        for i in r["Instances"]:
            return i

    return None


def hosts_contains(name: str) -> bool:
    try:
        with open("/etc/hosts") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if name in s.split():
                    return True
    except Exception:
        pass
    return False


def show_instance(inst):
    print()
    print("Instance details")
    print("----------------")
    print(f"InstanceId : {inst['InstanceId']}")
    print(f"State      : {inst['State']['Name']}")
    print(f"Type       : {inst['InstanceType']}")
    print(f"KeyName    : {inst.get('KeyName')}")
    print(f"Public IP  : {inst.get('PublicIpAddress')}")
    print()


def countdown_abort(seconds: int):
    if not sys.stdin.isatty():
        return

    print(f"Terminating in {seconds} seconds — press any key to abort")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        for remaining in range(seconds, 0, -1):
            print(f"  {remaining}…", end="", flush=True)

            rlist, _, _ = select.select([sys.stdin], [], [], 1)

            if rlist:
                sys.stdin.read(1)  #-jc consume one char
                print("\nAborted by user.")
                sys.exit(1)

            print("\r", end="", flush=True)

        print("Proceeding.")

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    parser = argparse.ArgumentParser(description="Terminate EC2 instance by name")
    parser.add_argument("name", help="Instance Name tag")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    parser.add_argument("--region", default=DEFAULT_REGION)

    args = parser.parse_args()

    ec2 = boto3.client("ec2", region_name=args.region)

    inst = find_instance(ec2, args.name)
    if not inst:
        print(f"Instance '{args.name}' not found.")
        sys.exit(1)

    show_instance(inst)

    #-jc hosts safety check
    if hosts_contains(args.name):
        print(f"WARNING: '{args.name}' still present in /etc/hosts")

    #-jc confirmation
    if not args.yes:
        answer = input("Type 'yes' to terminate: ").strip().lower()
        if answer != "yes":
            print("Aborted.")
            sys.exit(1)
    else:
        #-jc safety pause only in --yes mode
        countdown_abort(5)

    print("Terminating…")

    ec2.terminate_instances(InstanceIds=[inst["InstanceId"]])

    print("Termination requested.")


if __name__ == "__main__":
    main()

