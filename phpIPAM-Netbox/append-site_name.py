import json

file_path_vlan_usdc1 = r'c:\temp-python\phpipam\vlan-usdc1.json'
file_path_vlan_usdc2 = r'c:\temp-python\phpipam\vlan-usdc2.json'
file_path_vlan_all = r'c:\temp-python\phpipam\vlans.json'

new_file_path_vlan_usdc1 = r'c:\temp-python\phpipam\new_vlan-usdc1.json'
new_file_path_vlan_usdc2 = r'c:\temp-python\phpipam\new_vlan-usdc2.json'
new_file_path_vlan_all = r'c:\temp-python\phpipam\new_vlans.json'


def add_site(old_file_path, new_file_path, site):
    with open(old_file_path, "r") as old_file:
        vlans = json.load(old_file)
        for each_vlan in vlans:
            each_vlan["site_name"] = site
    with open(new_file_path, "w") as new_file:
        json.dump(vlans, new_file, indent=2)
    return

add_site(file_path_vlan_usdc1, new_file_path_vlan_usdc1, "AMUSDC1")
add_site(file_path_vlan_usdc2, new_file_path_vlan_usdc2, "AMUSDC2")

with open(file_path_vlan_all, "r") as old_file:
    vlans = json.load(old_file)
    for each_vlan in vlans:
        if str(each_vlan["domainId"]).strip() == "1":
            each_vlan["site_name"] = "Default"
        elif str(each_vlan["domainId"]).strip() == "2":
            each_vlan["site_name"] = "AMUSDC1"
        elif str(each_vlan["domainId"]).strip() == "3":
            each_vlan["site_name"] = "AMUSDC2"
        else:
            each_vlan["site_name"] = "Unknown"
    with open(new_file_path_vlan_all, "w") as new_file:
        json.dump(vlans, new_file, indent=2)