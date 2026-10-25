#Name:Murad Corchado | Student ID(carleton): 101392887 
import sys
import json
import xml.etree.ElementTree as ET
import yaml
import requests
from pathlib import Path
class BadInputFile(Exception):
    """Raised when a bad file is sent"""

class Device:

    def __init__(self, hostname,ip,ports=24):
        self.hostname=hostname
        self.ip=ip
        self.ports=ports

xml_file= Path("PA2_sample1.xml")

yaml_file= Path("PA2_policy.yaml")

if xml_file.exists():
    tree = ET.parse(xml_file)
    root = tree.getroot()
    site_name=root.get("site")#the site
    print(site_name)
    skipped_devices=0
    total_devices=0
    required_owner=True
    for device in root.findall("device"):
        device_id= device.get("id")
        device_role=device.get("role")
        device_os=device.get("os")
        find_owner= device.find("owner")
        if find_owner is not None:
            print(f"{device_id} owner is: {find_owner.text}")
        else:
            print(f"{device_id} has no owner")
            required_owner=False
        if device_id is not None:
            total_devices+=1
        else:
            skipped_devices+=1
            continue    
        
        print(f"Device id is: {device_id} using version {device_os} and its role is: {device_role}\n")

        for interfaces in device.findall("interface"):
            interface_name= interfaces.get("name")
            interface_status=interfaces.get("status")
            if interface_status=="up":
                print(f"{interface_name} is up")
            elif interface_status == "down":
                print(f"{interface_name} is down")
            else:
                print(f"{interface_name} is {interface_status}")

    
else:
    print(f"{xml_file} does not exist")

print(f"nums of total devices is {total_devices}")
print(f"nums of skipped devices is {skipped_devices}")
if yaml_file.exists():
    with open(yaml_file, "r") as f:
        yaml_config=yaml.safe_load(f)
        
else:
    print(f"{yaml_file} does not exist")


