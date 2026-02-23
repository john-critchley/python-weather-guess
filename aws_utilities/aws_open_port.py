#!/usr/bin/env python3

import sys
import socket
import boto3
import ipaddress


#-jc resolve host → CIDR
def resolve_to_cidr(target: str) -> str:
    if "/" in target:
        return target

    if target.lower() == "any":
        return "0.0.0.0/0"

    ip = socket.gethostbyname(target)
    return f"{ip}/32"


#-jc get primary security group for instance
def get_security_group(ec2, instance_id: str) -> str:
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    return resp["Reservations"][0]["Instances"][0]["SecurityGroups"][0]["GroupId"]


#-jc remove existing rules for this port
def flush_port(ec2, sg_id: str, port: int):
    sg = ec2.describe_security_groups(GroupIds=[sg_id])["SecurityGroups"][0]

    perms_to_remove = []

    for perm in sg.get("IpPermissions", []):
        if perm.get("FromPort") == port and perm.get("ToPort") == port:
            perms_to_remove.append(perm)

    if perms_to_remove:
        ec2.revoke_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=perms_to_remove,
        )
        print(f"Flushed existing rules for TCP {port}")
    else:
        print(f"No existing rules to flush for TCP {port}")


def main():
    args = sys.argv[1:]

    flush = False
    if "--flush" in args:
        flush = True
        args.remove("--flush")

    if len(args) != 3:
        print("Usage:")
        print("  aws_open_port.py <instance|hostname> <port> <ip-or-host> [--flush]")
        sys.exit(1)

    target_host, port_str, allowed = args
    port = int(port_str)

    #-jc reuse your existing credential model
    ec2 = boto3.client("ec2")

    #-jc resolve instance id via your hosts file logic expectation
    try:
        import subprocess

        inst = subprocess.check_output(
            ["getent", "hosts", target_host],
            text=True,
        )
        instance_id = inst.strip().split()[-1]
    except Exception:
        print(f"Could not resolve instance id for {target_host}")
        sys.exit(1)

    cidr = resolve_to_cidr(allowed)

    sg_id = get_security_group(ec2, instance_id)
    print(f"Using security group {sg_id}")

    if flush:
        flush_port(ec2, sg_id, port)

    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": port,
                    "ToPort": port,
                    "IpRanges": [{"CidrIp": cidr}],
                }
            ],
        )
        print(f"Opened TCP {port} to {cidr}")

    except ec2.exceptions.ClientError as e:
        if "InvalidPermission.Duplicate" in str(e):
            print("Rule already exists — OK")
        else:
            raise


if __name__ == "__main__":
    main()

