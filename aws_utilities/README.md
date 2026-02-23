# Some small utilities to make it work

- awsctl.py - start and stop aws EC2 host
- awsdeletehost.py - terminate EC2 instance
- awslaunch.py - provision EC2 instance
- aws_open_port.py - open ports to incoming TCP traffic without GUI

awsctl.py uses udp port 5 to update /etc/hosts

## hosts file

The assumption I make is that my /etc/hosts file is this format

<IP address> <short name> [other names...] <AWS EC2 Instance ID>

requests using boto3 look up the EC2 Instance ID from the last line of hosts.

### examples
awslaunch.py weather t3.medium
(default profile is North Virginia)
provision a t3.medium instance;
it will give a minimum hosts line in its output, including provisioned IP address,
short name from command line and EC2 Instance ID
The ssh key is written into ~/.ssh - the file name is the short name of the host.
I usually add this to my ssh agent.

awsdeletehost.py weather
gets rid of EC2 instance

aws_open_port.py weather 8088 any --flush
This will allow tcp connections from "any" ip adderess to port 8088 on host weather.
Because "--flush" is given any other rules for that port are removed.

## ansible usage of these scripts

You'll either need to change or override
    aws_scripts_dir: "/home/john/aws"
to the location these scripts are.
ansible compose uses awslaunch.py and aws_open_port.py.

When I provision a host I have been doing something like...
echo /home/john/aws/awsdeletehost.py weather | at teatime tomorrow
so I don't leave lots of expensive instances running.

# k8s

The host should really be provosioned using Kubernetes.
Watch this space as I'd like to get to grips with it, although
I didn't get chance for this exercise.
