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
    xml_dict = {}
    roles_dict={}
    interfaces_dict= {"up":0, "down":0,"other":0}#Values here can be hard coded since there is only up and down and other statuses
    skipped_devices=0
    total_devices=0
    required_owner=True

    for device in root.findall("device"):
        device_id= device.get("id")
        device_role=device.get("role")
        device_os=device.get("os")
        find_owner= device.find("owner")
        
        #Fix this part
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

        if device_role in roles_dict:
            roles_dict[device_role]+=1
        else:
            roles_dict[device_role]=1
        

        for interfaces in device.findall("interface"):
            interface_name= interfaces.get("name")
            interface_status=interfaces.get("status")
            
            if interface_status in interfaces_dict:
                interfaces_dict[interface_status] +=1
            else:
                interfaces_dict["other"] +=1

        print(f"Device id is: {device_id} using version {device_os} and its role is: {device_role} with a status of {interface_status}\n")
else:
    print(f"{xml_file} does not exist")


xml_dict["site"] = site_name
xml_dict["total_devices"] = total_devices
xml_dict["skipped_devices"] = skipped_devices
xml_dict["roles"]= roles_dict
xml_dict["interfaces"]= interfaces_dict
print(xml_dict)


with open("audit.json","w",encoding="utf-8") as f:
    json.dump(xml_dict,f, indent=1,ensure_ascii=False)


if yaml_file.exists():
    with open(yaml_file, "r") as f:
        yaml_config=yaml.safe_load(f)  
else:
    print(f"{yaml_file} does not exist")


