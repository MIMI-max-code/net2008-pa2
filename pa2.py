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

xml_dict = {}
roles_dict={}
interfaces_dict= {"up":0, "down":0,"other":0}#Values here can be hard coded since there is only up and down and other statuses
skipped_devices=0
total_devices=0
violations=[]


with open("PA2_policy.yaml", "r") as f:
    yaml_config=yaml.safe_load(f)


if xml_file.exists():
    tree = ET.parse(xml_file)
    root = tree.getroot()
    site_name=root.get("site")#the site
    for device in root.findall("device"):
        
        device_id= device.get("id")
        device_role=device.get("role")
        device_os=device.get("os")
        find_owner= device.find("owner")
        
        #Fix this part
        if 'require_owner' in yaml_config:
            if yaml_config['require_owner'] is True:
                #if the owner tag has a string of spaces, strip will decompress it to empty string
                if find_owner is None or find_owner.text is None or find_owner.text.strip() == "":
                    missing_owner_dict = {"device" : device_id, "type" : "missing_owner"}
                    violations.append(missing_owner_dict)

        if device_id is not None:
            total_devices+=1
        else:
            skipped_devices+=1
            continue

        if device_role in roles_dict:
            roles_dict[device_role]+=1
        else:
            roles_dict[device_role]=1

        if 'min_os' in yaml_config:
            if device_role not in yaml_config['min_os']:
                unknown_role_dict = {"device" : device_id , "type" : "unknown_role", "role": device_role}
                violations.append(unknown_role_dict)
        
        interfaces_down_count=0
        for interfaces in device.findall("interface"):
            interface_status=interfaces.get("status")
            
            if interface_status in interfaces_dict:
                interfaces_dict[interface_status] +=1
            else:
                interfaces_dict["other"] +=1

            if interface_status == "down":
                interfaces_down_count+=1
        if 'max_down_interfaces' in yaml_config:
            if interfaces_down_count > yaml_config['max_down_interfaces']:
                max_down_dict = {"device" : device_id, "type" : "too_many_down", "down" : interfaces_down_count}
                violations.append(max_down_dict)
            
        
    
else:
    print(f"{xml_file} does not exist")


xml_dict["site"] = site_name
xml_dict["total_devices"] = total_devices
xml_dict["skipped_devices"] = skipped_devices
xml_dict["roles"]= roles_dict
xml_dict["interfaces"]= interfaces_dict
xml_dict["violations"]= violations
print(xml_dict)


with open("audit.json","w",encoding="utf-8") as f:
    json.dump(xml_dict,f, indent=1,ensure_ascii=False)





        


