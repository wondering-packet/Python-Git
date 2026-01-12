import json

def parse_vlan_file(file_path):
    vlan_list = []
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
        i = 0
        while i < len(lines):
            if lines[i].lower().startswith("vlan"):
                try:
                    vlan_id = int(lines[i].split()[1])
                    vlan_name = "Name-Undefined"
                    if i + 1 < len(lines) and lines[i + 1].lower().startswith("name"):
                        vlan_name = lines[i + 1].split(" ", 1)[1]
                        i += 2
                    else:
                        i += 1
                    vlan_list.append({"number": vlan_id, "name": vlan_name})
                except (IndexError, ValueError):
                    i += 1  # Skip malformed entries
            else:
                i += 1
    return vlan_list

# Example usage
file_path_usdc1 = r'c:\temp-python\vlan-usdc1.txt'
file_path_usdc2 = r'c:\temp-python\vlan-usdc2.txt'
vlan_data_usdc1 = parse_vlan_file(file_path_usdc1)
vlan_data_usdc2 = parse_vlan_file(file_path_usdc2)

file_path_vlan_usdc1 = r'c:\temp-python\phpipam\vlan-usdc1.json'
with open(file_path_vlan_usdc1, "w") as f:
    json.dump(vlan_data_usdc1, f, indent=2)

file_path_vlan_usdc2 = r'c:\temp-python\phpipam\vlan-usdc2.json'
with open(file_path_vlan_usdc2, "w") as f:
    json.dump(vlan_data_usdc2, f, indent=2)