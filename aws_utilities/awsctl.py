#!/usr/bin/python

import sys
import json
import boto3
import socket
import time


def send_udp_with_retry(message, address='127.0.0.1', port=5, timeout=1, max_retries=3):
    retries = 0
    response = None

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the socket timeout
    udp_socket.settimeout(timeout)

    while retries < max_retries:
        try:
            # Send the UDP packet
            udp_socket.sendto(message.encode(), (address, port))

            # Wait for the response
            response, _ = udp_socket.recvfrom(1024)

            # If a response is received, break out of the loop
            if response:
                response=response.decode()
                break
        except socket.timeout:
            # If a timeout occurs, increment the retries counter and try again
            retries += 1
            print(f"No response received. Retrying ({retries}/{max_retries})...")
            time.sleep(timeout)  # Wait before retrying

    # Close the socket
    udp_socket.close()

    return response

def lookup_instance(client, instance):
    response=client.describe_instances(InstanceIds=[instance])
    return response['Reservations']

if __name__=="__main__":
    prog,*args=(sys.argv)

    # Parse arguments - profile is optional
    if len(args) == 3:
        verb, host, profile = args
    elif len(args) == 2:
        verb, host = args
        profile = None
    else:
        print('Usage: awsctl.py <start|stop> <host> [profile]')
        sys.exit(1)

    #print(verb,host)
    verbmap=dict(start=True, stop=False)
    try:
        start=verbmap[verb]
    except KeyError as e:
        print('Only valid verbs:', *(verbmap.keys()))
        sys.exit(1)
    message = f"canon {host}"
    response = send_udp_with_retry(message)
    response_status=response[0]
    response_msg=response[1:].strip()
    #print("canon response:", response_status, response_msg)
    if response_status!='L':
        print(response_msg)
        sys.exit(1)
    if profile:
        session = boto3.Session(profile_name=profile)
        client = session.client('ec2')
    else:
        client = boto3.client('ec2')
    action=client.start_instances if start else client.stop_instances
    action(InstanceIds=[response_msg])

    # Wait for the instance to enter the right state
    waiter = client.get_waiter('instance_running' if start else 'instance_stopped')
    waiter.wait(InstanceIds=[response_msg])

    if start:
        addr=lookup_instance(client, response_msg)[0]['Instances'][0]['PublicIpAddress']
        print(addr)

    message = f'host {response_msg} {addr}' if start else f'disable {response_msg}'
    response = send_udp_with_retry(message)
    response_status=response[0]
    response_msg=response[1:].strip()
    #print(f"host response {response_status} {response_msg}")
    if response_status!=('U' if start else 'K'):
        print(response_msg)
        sys.exit(1)
    
    message = f'save'
    response = send_udp_with_retry(message)
    response_status=response[0]
    response_msg=response[1:].strip()
    #print(f"host response {response_msg}")

    if response_status!='S':
        print(response_msg)
        sys.exit(1)
    sys.exit(0)
