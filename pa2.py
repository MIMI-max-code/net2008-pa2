#Name:Murad Corchado | Student ID: 041221849 
import sys
import json
import xml.etree.ElementTree as ET
import yaml
from pathlib import Path

class MappingError(Exception):
    """Raised when a policy file is not properly mapped"""

class Device:
    """Initializes each device"""
    def __init__(self, id,role,os,owner,interfaces):
        self.id=id
        self.role=role
        self.os=os
        self.owner=owner
        self.interfaces=interfaces

    def check_device(self, yaml_policy):
        """Checks a device against a policy"""
        device_violations = []

        #Checks if owner is missing
        if yaml_policy.get('require_owner') is True:
            if self.owner is None or self.owner.strip() == "":
                missing_owner_dict = {"device" : self.id, "type" : "missing_owner"}
                device_violations.append(missing_owner_dict)

        #Checks if the role is unknown
        if 'min_os' in yaml_policy:
            if self.role not in yaml_policy['min_os']:
                unknown_role_dict = {"device" : self.id , "type" : "unknown_role", "role": self.role}
                device_violations.append(unknown_role_dict)
            else:
            #Checks if the os version is outdated
                yaml_list = parse_version(yaml_policy['min_os'][self.role])
                device_os_list=parse_version(self.os)
                equal_version_length(yaml_list,device_os_list)
                if device_os_list < yaml_list:
                    os_outdated_dict={"device" : self.id, "type" : "os_outdated", "found" : self.os, "required" : yaml_policy['min_os'][self.role]}
                    device_violations.append(os_outdated_dict)

        interfaces_down_count=0
        #Loops through the interfaces of the device and checks if more than the maximum of downed interfaces are down
        for interfaces in self.interfaces:
            interface_status=interfaces.get("status")
            
            if interface_status == "down":
                interfaces_down_count+=1
        if 'max_down_interfaces' in yaml_policy:
            if interfaces_down_count > yaml_policy['max_down_interfaces']:
                max_down_dict = {"device" : self.id, "type" : "too_many_down", "down" : interfaces_down_count}
                device_violations.append(max_down_dict)
        return device_violations
        
        

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

def main():
    
    if len(sys.argv)!= 3:
        print("usage: python pa2.py DEVICES.xml POLICY.yaml")
        sys.exit(2)

    xml_file=sys.argv[1] #Correlates to the DEVICE.xml
    yaml_file=sys.argv[2] #Correlates to the POLICY.yaml

    try:
        parsed_xml_file=parse_xml(xml_file)
        parsed_yaml_file=parse_yaml(yaml_file)
        #Ensures that even if policy is empty, the program still works
        if parsed_yaml_file is None:
            parsed_yaml_file= {}
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

    xml_dict = {}
    roles_dict={}
    interfaces_dict= {"up":0, "down":0,"other":0}
    skipped_devices=0
    total_devices=0
    violations=[]
    compliant_list=[]
    compliant_counter=0
    
    site_name=parsed_xml_file.get("site") 
    for device in parsed_xml_file.findall("device"):
        
        device_id= device.get("id")
        device_role=device.get("role")
        device_os=device.get("os")
        find_owner= device.find("owner")
        owner_tag=None
        if find_owner is not None:
            owner_tag = find_owner.text
        
        if device_id is not None:
            total_devices+=1
        else:
            skipped_devices+=1
            continue
    
        if device_role in roles_dict:
            roles_dict[device_role]+=1
        else:
            roles_dict[device_role]=1
            
        device_interfaces= device.findall("interface")
        for interfaces in device_interfaces:
            interface_status=interfaces.get("status")
                
            if interface_status in interfaces_dict:
                interfaces_dict[interface_status] +=1
            else:
                interfaces_dict["other"] +=1

        device_check= Device(device_id,device_role,device_os,owner_tag,device_interfaces)
        device_violations= device_check.check_device(parsed_yaml_file)
    
        if len(device_violations)> 0:
            violations.extend(device_violations)
        else:
            compliant_list.append(device_id)
            compliant_counter+=1
    compliant_list.sort()

    xml_dict["site"] = site_name
    xml_dict["total_devices"] = total_devices
    xml_dict["skipped_devices"] = skipped_devices
    xml_dict["roles"]= roles_dict
    xml_dict["interfaces"]= interfaces_dict
    xml_dict["violations"]= violations
    xml_dict["compliant"]= compliant_list

    print("Script run Successfully")
    print(f"Location: {site_name} | Total devices: {total_devices} | Skipped devices: {skipped_devices} | Compliant devices: {compliant_counter} | Number of violations: {len(violations)}")

    
    with open("audit.json","w",encoding="utf-8") as f:
        json.dump(xml_dict,f, indent=1,ensure_ascii=False)



if __name__ == "__main__":
    main()
        


