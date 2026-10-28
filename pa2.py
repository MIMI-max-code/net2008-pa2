#Name:Murad Corchado | Student ID(carleton): 101392887 
import sys
import json
import xml.etree.ElementTree as ET
import yaml
from pathlib import Path
class MappingError(Exception):
    """Raised when a policy file is not properly mapped"""

class Device:

    def __init__(self, id,role,os,owner,interfaces):
        self.id=id
        self.role=role
        self.os=os
        self.owner=owner
        self.interfaces=interfaces

def parse_xml(xml_file):
    """Parses an xml file"""
    file_xml = Path(xml_file)
    tree = ET.parse(file_xml)
    root = tree.getroot()
    return root

def parse_yaml(yaml_file):
    """Parses a yaml file"""
    with open(yaml_file, "r") as f:
        yaml_config=yaml.safe_load(f)
    return yaml_config

def parse_version(string):
    """This will be used to split string versions into a list of ints"""
    split= string.split(".")
    for i in range(len(split)):
        split[i]=int(split[i])
    return split

def equal_version_length(list1,list2):
    """Used when version lengths are not equal"""
    if len(list1) < len(list2):
        while len(list1)< len(list2):
            list1.append(0)
    else:
        while len(list2)< len(list1):
            list2.append(0)

xml_file= Path("PA2_sample1.xml")

xml_dict = {}
roles_dict={}
interfaces_dict= {"up":0, "down":0,"other":0}#Values here can be hard coded since there is only up and down and other statuses
skipped_devices=0
total_devices=0
violations=[]
compliant_list=[]


with open("PA2_policy.yaml", "r") as f:
    yaml_config=yaml.safe_load(f)


if xml_file.exists():
    tree = ET.parse(xml_file)
    root = tree.getroot()
    site_name=root.get("site")#the site
    for device in root.findall("device"):
        compliant_device= True
        device_id= device.get("id")
        device_role=device.get("role")
        device_os=device.get("os")
        find_owner= device.find("owner")
        
        
        if 'require_owner' in yaml_config:
            if yaml_config['require_owner'] is True:
                #if the owner tag has a string of spaces, strip will decompress it to empty string
                if find_owner is None or find_owner.text is None or find_owner.text.strip() == "":
                    missing_owner_dict = {"device" : device_id, "type" : "missing_owner"}
                    violations.append(missing_owner_dict)
                    compliant_device= False

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
                compliant_device=False
            else:
                yaml_list = parse_version(yaml_config['min_os'][device_role])
                device_os_list=parse_version(device_os)
                equal_version_length(yaml_list,device_os_list)
                if device_os_list < yaml_list:
                    os_outdated_dict={"device" : device_id, "type" : "os_outdated", "found" : device_os, "required" : yaml_config['min_os'][device_role]}
                    violations.append(os_outdated_dict)
                    compliant_device=False
        
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
                compliant_device=False

        if compliant_device == True:
            compliant_list.append(device_id)

    compliant_list.sort()

            
        
    
else:
    print(f"{xml_file} does not exist")



xml_dict["site"] = site_name
xml_dict["total_devices"] = total_devices
xml_dict["skipped_devices"] = skipped_devices
xml_dict["roles"]= roles_dict
xml_dict["interfaces"]= interfaces_dict
xml_dict["violations"]= violations
xml_dict["compliant"]= compliant_list
print(xml_dict)


with open("audit.json","w",encoding="utf-8") as f:
    json.dump(xml_dict,f, indent=1,ensure_ascii=False)



def main():
    
    
    if len(sys.argv)!= 3:
        print("usage: python pa2.py DEVICES.xml POLICY.yaml")
        sys.exit(2)

    xml_file=sys.argv[1] #Correlates to the DEVICE.xml
    yaml_file=sys.argv[2] #Correlates to the POLICY.yaml

    try:
        parsed_xml_file=parse_xml(xml_file)
        parsed_yaml_file=parse_yaml(yaml_file)
        
        #Checks if the policy file is not a dict
        if not isinstance(parsed_yaml_file,dict):
            raise MappingError(yaml_file)
    except FileNotFoundError as e:
        print(f"{e.filename} could not be found")
        sys.exit(1)
    except ET.ParseError as xml_error:
        print(f"{xml_file} has a parsing error: {xml_error}")
        sys.exit(1)
    except yaml.YAMLError as yaml_error:
        print(f"{yaml_file} has a parsing error: {yaml_error}")
        sys.exit(1)
    except MappingError as error:
        print(f"{error} policy file is not properly mapped")
        sys.exit(1)

    
    



if __name__ == "__main__":
    main()
        


