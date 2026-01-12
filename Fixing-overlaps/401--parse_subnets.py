'''
processes 2 csv files: netbox_retail_stores_prefixes.csv & 400-retail_filtered_vlans.csv
netbox_retail_stores_prefixes.csv is a manually parsed file with duplicates removed.
400-retail_filtered_vlans.csv is another processed csv file with any invalid vlans removed
(i.e. vlans that don't have a supernet). it still contains duplicates.

script does two things:
1. ensures the subnet (/26) has a valid supernet (/24). skips any subnets which doesn't have a supernet.
2. since this script checks the vlans against the prefixes file which doesn't have duplicates, 
the new output file contains the subnets (/26) which has duplicates removed.
'''
import pandas as pd
import ipaddress

# Example usage:
file1 = r"c:\temp\netbox\netbox_retail_stores_prefixes.csv"  # Path to the first CSV file (Supernets)
file2 = r"c:\temp\netbox\400-retail_filtered_vlans.csv"  # Path to the second CSV file (VLANs)
file3 = r"c:\temp\netbox\401-retail_filtered_subnets.csv"  # Path for the output filtered CSV

def load_data(file_path):
    # Load the data and strip any extra spaces from column names
    df = pd.read_csv(file_path, encoding='latin1')
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespaces from column names
    return df

def is_subnet_in_supernet(subnet, supernet):
    try:
        # Convert the subnet and supernet to ipaddress objects
        subnet_ip = ipaddress.IPv4Network(subnet)
        supernet_ip = ipaddress.IPv4Network(supernet)
        
        # Check if the subnet is within the supernet
        return subnet_ip.subnet_of(supernet_ip)
    except ValueError as e:
        # If the subnet or supernet is in an invalid format, return False
        print(f"Invalid subnet or supernet format: {subnet} / {supernet}")
        return False

def filter_vlans_by_supernet(file1, file2, file3):
    # Load the data from both files
    df_supernets = load_data(file1)
    df_vlans = load_data(file2)
    
    # Create a list to store filtered VLANs
    filtered_vlans = []
    
    # Iterate over the rows in the VLAN dataframe
    for _, vlan_row in df_vlans.iterrows():
        network_name = vlan_row['Network Name']
        vlan_network_id = vlan_row['VLAN Network ID']
        
        # Get the matching supernets for this network_name
        matching_supernets = df_supernets[df_supernets['name'] == network_name]
        
        # If no matching supernets are found, skip this VLAN
        if matching_supernets.empty:
            continue
        
        # Check if the VLAN network ID is within any of the supernets for the network_name
        valid_supernet = False
        for _, supernet_row in matching_supernets.iterrows():
            supernet = supernet_row['prefix']
            if is_subnet_in_supernet(vlan_network_id, supernet):
                valid_supernet = True
                break
        
        # If the VLAN belongs to a valid supernet, add it to the filtered list
        if valid_supernet:
            filtered_vlans.append(vlan_row)
        else:
            print(f"VLAN {vlan_network_id} does not match any valid supernet for network {network_name}")
    
    # Create a DataFrame from the filtered VLANs and drop duplicates
    filtered_df = pd.DataFrame(filtered_vlans).drop_duplicates()
    
    # Write the filtered data to a new CSV file
    filtered_df.to_csv(file3, index=False)
    print(f"Filtered VLANs saved to {file3}")

filter_vlans_by_supernet(file1, file2, file3)
