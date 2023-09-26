import socket
import json
import sys
import time
import subprocess
import re

def get_ip():
    output = subprocess.getoutput("/usr/sbin/ifconfig wfan0")

    # starts with 2020:
    match = re.search(r"inet6 2020:([0-9a-f:]+) ", output)

    if match:
        return "2020:" + match.group(1)
    
    return None

def send(payload):
    ip = get_ip()

    if not ip:
        raise Exception("No IPv6 address found")
        
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    payload = {
        "type": "broadcast",
        "data": payload,
        "timestamp": time.time(),
        "origin": get_ip()
    }

    print(payload)

    with open("neighbors.json", "r") as f:
        neighbors = json.load(f)["neighbors"]

    for neighbor in neighbors:
        sock.sendto(json.dumps(payload).encode(), (neighbor, 9999))

def main():
    send(sys.stdin.read())