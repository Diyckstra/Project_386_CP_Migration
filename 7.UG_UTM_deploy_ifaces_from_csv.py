from functions import *
from functions_UG import UG_UTM_get_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_7}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
logger.info(f"Script starts")

# Open CSV file
dict_ip_plan = []
try:
    with open(f"{path['input_path']}/{ip_plan_selected}", mode ='r', encoding = 'utf-8-sig', newline = '') as csvfile:
        csvFile = csv.reader(csvfile, delimiter=';', dialect='excel')

        for count, line in enumerate(csvFile):
            if count != 0:
                tmp = {
                    'physical': line[0],
                    'logical':  line[1],
                    'cp_iface': line[2],
                    '0_ip_cp':  line[3],
                    '1_ip_cp':  line[4],
                    '2_ip_cp':  line[5],
                    'zone':     line[6],
                    '0_ip_ug':  line[7],
                    '1_ip_ug':  line[8],
                    '2_ip_ug':  line[9],
                    'mask':     line[10]
                }
                dict_ip_plan.append(tmp)
    logger.info(f"CSV IP plan file {path['input_path']}/{ip_plan_selected} read")

except FileNotFoundError:
    logger.error(f"CSV IP plan file {path['input_path']}/{ip_plan_selected} not found. Program exit")
    quit()

except IndexError:
    logger.error(f"CSV IP plan file {path['input_path']}/{ip_plan_selected} is written with the wrong title length. Program exit")
    quit()

# Get creds to UG UTM
try:
    with open(f"{path['input_path']}/{UG_UTM_selected_creds_file}") as file:
        R_UG_UTM = json.load(file)
    UG_UTM_fw_address   = R_UG_UTM["address"]
    UG_UTM_fw_api_port  = R_UG_UTM["port"]
    UG_UTM_user         = R_UG_UTM["user"]
    UG_UTM_password     = R_UG_UTM["password"]

    logger.info(f"Creds file {path['input_path']}/{UG_UTM_selected_creds_file} read")

# Credentials file not found
except FileNotFoundError:
    logger.error(f"Creds file {path['input_path']}/{UG_UTM_selected_creds_file} not found. Program exit")
    quit()

# No node is available
except BlockingIOError:
    logger.error(f"UG UTM {UG_UTM_fw_address} is unavailable. Program exit")
    quit()

#-----------------------------------------------------------------------------------------------------------------------------------------

# Get auth token
UG_UTM_server, UG_UTM_auth_token = UG_UTM_get_token(UG_UTM_fw_address, UG_UTM_fw_api_port, UG_UTM_user, UG_UTM_password)
if UG_UTM_auth_token:
    logger.success(f"Authorization token received from UG UTM {UG_UTM_fw_address}")
else:
    logger.error(f"Token not received, error: {UG_UTM_server}")
    quit()

try:
    node_name = UG_UTM_server.v2.core.nodes.list(UG_UTM_auth_token)

    # Both nodes are available
    if node_name[0]['status'] == 'online' and node_name[1]['status'] == 'online':
        logger.info(f"Both nodes are available")

        if node_name[0]['license'] == 'active' and node_name[1]['license'] == 'active':
            logger.info(f"Both nodes are activated")

    # First node available
    elif node_name[0]['status'] != 'online':
        logger.error(f"{node_name[0]['cc_node_name']} <{node_name[0]['name']}> <{node_name[0]['display_name']}> is {node_name[0]['status']}. Program exit")
        try:
            UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
            logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
        except:
            logger.error(f"Trouble with release token")
        quit()

    # Second node is available
    elif node_name[1]['status'] != 'online':
        logger.error(f"{node_name[1]['cc_node_name']} <{node_name[1]['name']}> <{node_name[1]['display_name']}> is {node_name[1]['status']}. Program exit")
        try:
            UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
            logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
        except:
            logger.error(f"Trouble with release token")
        quit()

    # Verify node names
    if node_name[0]['cc_node_name'] == "node_1" and node_name[1]['cc_node_name'] == "node_2":
        node_name_1 = node_name[0]['name']
        node_name_2 = node_name[1]['name']
        disp_node_name_1 = node_name[0]['display_name']
        disp_node_name_2 = node_name[1]['display_name']
        logger.info(f"Node names are defined: {node_name_1} ({disp_node_name_1}) and {node_name_2} ({disp_node_name_2})")

    elif node_name[1]['cc_node_name'] == "node_1" and node_name[0]['cc_node_name'] == "node_2":
        node_name_1 = node_name[1]['name']
        node_name_2 = node_name[0]['name']
        disp_node_name_1 = node_name[1]['display_name']
        disp_node_name_2 = node_name[0]['display_name']
        logger.info(f"Node names are defined: {node_name_1} ({disp_node_name_1}) and {node_name_2} ({disp_node_name_2})")
    else:
        logger.error(f"There is some problem with determining the names of the nodes. Program exit")
        quit()

    result_cluster_list = UG_UTM_server.v1.ha.clusters.list(UG_UTM_auth_token)
    if len(result_cluster_list) > 1:
        logger.error(f"More than one cluster detected")
        try:
            UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
            logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
        except:
            logger.error(f"Trouble with release token")
        quit()
    else:
        logger.success(f"One cluster detected: {result_cluster_list[0]['name']}")
        cluster_id = result_cluster_list[0]["id"]

# Credentials file not found
except FileNotFoundError:
    logger.error(f"Creds file {path['input_path']}/{UG_UTM_selected_creds_file} not found. Program exit")
    quit()

# No node is available
except BlockingIOError:
    logger.error(f"UG UTM {UG_UTM_fw_address} is unavailable. Program exit")
    quit()

#-----------------------------------------------------------------------------------------------------------------------------------------
# Get & Check Zones
logger.info(f"Get & check zones")
# Read Zones from UTM
zones_from_utm = UG_UTM_server.v1.netmanager.zones.list(UG_UTM_auth_token)
dict_zones_id = {}
missing_vrrp_in_zone = []
for utm_zone in zones_from_utm:
    if utm_zone["name"][0:3] == MC_PREFIX:
        dict_zones_id[utm_zone["name"].replace(MC_PREFIX, "")] = utm_zone["id"]

        # Checking existing zones for the presence of the VRRP service
        for services_access in utm_zone["services_access"]:
            if services_access["service_id"] == 7 and not services_access["enabled"]:
                missing_vrrp_in_zone.append(utm_zone["name"].replace(MC_PREFIX, ""))

# Checking for missing zones in a CSV file
missing_zones = []
for csv_line in dict_ip_plan:
    if csv_line["zone"] and csv_line["zone"] not in dict_zones_id and csv_line["zone"] not in missing_zones:
        missing_zones.append(csv_line["zone"])

if missing_zones:
    logger.error("There are no MC zones on UTM that are present in the CSV file. Program exit")
    logger.info(f"Missing MC zones: {missing_zones}")
    try:
        UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
        logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
    except:
        logger.error(f"Trouble with release token")
    quit()
else:
    logger.success(f"The CSV file contains the necessary zones")

# Checking existing zones for the presence of the VRRP service
if missing_vrrp_in_zone:
    logger.error("In some zones VRRP is not enabled. Program exit")
    logger.info(f"MC zones with missed VRRP service: {missing_vrrp_in_zone}")
    try:
        UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
        logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
    except:
        logger.error(f"Trouble with release token")
    quit()
else:
    logger.success(f"VRRP service is enabled on zones")

#----------------------------------------------------------------------------------------------
# 1. Deploy Aggregate interface
logger.info("Searching aggregated interfaces")

# Find all bond interface
dict_bonds = {}
for line_in_dict_plan in dict_ip_plan:
    if (line_in_dict_plan['physical'][0:4] == 'bond' and 
        line_in_dict_plan['physical'].find('.') == -1 and
        line_in_dict_plan['physical'] not in dict_bonds):
        dict_bonds[line_in_dict_plan['physical']] = {
            "members": [],
            "0_ip_ug": "",
            "1_ip_ug": "",
            "2_ip_ug": "",
            "mask": "",
            "zone": 0
            }

    elif (line_in_dict_plan['logical'][0:4] == 'bond' and 
        line_in_dict_plan['logical'].find('.') == -1 and
        line_in_dict_plan['logical'] not in dict_bonds):
        dict_bonds[line_in_dict_plan['logical']] = {
            "members": [],
            "0_ip_ug": "",
            "1_ip_ug": "",
            "2_ip_ug": "",
            "mask": "",
            "zone": 0
            }

# Fill dictionary with bonds
pop_numbers = []
for line_in_dict_bonds in dict_bonds:
    for count, line_in_dict_plan in enumerate(dict_ip_plan):

        # Fill members
        if line_in_dict_bonds == line_in_dict_plan['logical'] and line_in_dict_plan['logical'] != line_in_dict_plan['physical']:
            if line_in_dict_plan['physical'] not in dict_bonds[line_in_dict_bonds]["members"]:
                dict_bonds[line_in_dict_bonds]["members"].append(line_in_dict_plan['physical'])
            pop_numbers.append(count)

        elif line_in_dict_bonds == line_in_dict_plan['logical'] and line_in_dict_plan['logical'] == line_in_dict_plan['physical']:

            # Fill zone
            if line_in_dict_plan["zone"]:
                dict_bonds[line_in_dict_bonds]["zone"] = dict_zones_id[line_in_dict_plan["zone"]]

            # Fill IP
            if line_in_dict_plan["0_ip_ug"] or line_in_dict_plan["1_ip_ug"] or line_in_dict_plan["2_ip_ug"] or line_in_dict_plan["mask"]:

                # Not entered 0 IP
                while not line_in_dict_plan["0_ip_ug"]:
                    line_in_dict_plan["0_ip_ug"] = input(f"0 IP address not entered in the line number {count}, enter the correct address: ")

                # Not entered 1 IP
                while not line_in_dict_plan["1_ip_ug"]:
                    line_in_dict_plan["1_ip_ug"] = input(f"1 IP address not entered in the line number {count}, enter the correct address: ")

                # Not entered 2 IP
                while not line_in_dict_plan["2_ip_ug"]:
                    line_in_dict_plan["2_ip_ug"] = input(f"2 IP address not entered in the line number {count}, enter the correct address: ")

                # Not entered mask
                while not line_in_dict_plan["mask"]:
                    line_in_dict_plan["mask"] = input(f"IP mask not entered in the line number {count}, enter the correct mask: ")

                dict_bonds[line_in_dict_bonds]["0_ip_ug"], dict_bonds[line_in_dict_bonds]["mask"] = check_ip(count, line_in_dict_plan["0_ip_ug"], line_in_dict_plan["mask"])
                dict_bonds[line_in_dict_bonds]["1_ip_ug"], dict_bonds[line_in_dict_bonds]["mask"] = check_ip(count, line_in_dict_plan["1_ip_ug"], line_in_dict_plan["mask"])
                dict_bonds[line_in_dict_bonds]["2_ip_ug"], dict_bonds[line_in_dict_bonds]["mask"] = check_ip(count, line_in_dict_plan["2_ip_ug"], line_in_dict_plan["mask"])

                if not dict_bonds[line_in_dict_bonds]['zone']:
                    logger.warning(f"Zone not set for L3 interface {line_in_dict_bonds}")

            pop_numbers.append(count)

# Cleaning ip_plan_selected
count = 0
for one_pop_numbers in pop_numbers:
    dict_ip_plan.pop(one_pop_numbers-count)
    count += 1

# Deploy bond interfaces
if dict_bonds:
    logger.info(f"Aggregate Interfaces detected, deploy")
    for line_in_dict_bonds in dict_bonds:
        
        cluster_interface = {}
        interface_details_1 = {}
        interface_details_2 = {}
        interface_details = {
            "name": line_in_dict_bonds,
            "enabled": False,
            #"description": f'enabled:{(True if i["state"] == "on" else False)}',
            "zone_id": dict_bonds[line_in_dict_bonds]["zone"],
            "bonding": {
                "fail_over_mac": 0,
                "slaves": dict_bonds[line_in_dict_bonds]["members"],
                "updelay": 100,
                "downdelay": 200,
                "miimon": 100,
                "mode": 4,
                "lacp_rate": 0,
                "xmit_hash_policy": 0,
                }
            }

        # IP info
        if dict_bonds[line_in_dict_bonds]["0_ip_ug"] or dict_bonds[line_in_dict_bonds]["1_ip_ug"] or dict_bonds[line_in_dict_bonds]["2_ip_ug"] or dict_bonds[line_in_dict_bonds]["mask"]:
            interface_details["mode"] = "static"

            interface_details_1 = interface_details.copy()
            interface_details_2 = interface_details.copy()

            cluster_interface = {'interfaces': 
                [{'ifname': line_in_dict_bonds, 'node_name': node_name_1},
                 {'ifname': line_in_dict_bonds, 'node_name': node_name_2}],
                 'ipv4': ipaddress.IPv4Interface(f"{dict_bonds[line_in_dict_bonds]['0_ip_ug']}/{dict_bonds[line_in_dict_bonds]['mask']}").with_prefixlen }

            interface_details_1["ipv4"] = [ipaddress.IPv4Interface(f'{dict_bonds[line_in_dict_bonds]["1_ip_ug"]}/{dict_bonds[line_in_dict_bonds]["mask"]}').with_prefixlen]
            interface_details_2["ipv4"] = [ipaddress.IPv4Interface(f'{dict_bonds[line_in_dict_bonds]["2_ip_ug"]}/{dict_bonds[line_in_dict_bonds]["mask"]}').with_prefixlen]

            logger.info(f'A config for the interface {line_in_dict_bonds} with an IP address (vip: {dict_bonds[line_in_dict_bonds]["0_ip_ug"]}, node_1: {dict_bonds[line_in_dict_bonds]["1_ip_ug"]}, node_2: {dict_bonds[line_in_dict_bonds]["2_ip_ug"]}, mask: {dict_bonds[line_in_dict_bonds]["mask"]}) was been generated')

        else:
            interface_details["mode"] = "manual"

            interface_details_1 = interface_details.copy()
            interface_details_2 = interface_details.copy()

            logger.info(f"A config for the interface {line_in_dict_bonds} without an IP address has been generated")

        # Deploy bond on node 1
        try:
            result_1 = UG_UTM_server.v1.netmanager.interface.add.bond(UG_UTM_auth_token, node_name_1, line_in_dict_bonds, interface_details_1)
            if result_1 == line_in_dict_bonds:
                result_1_1 = UG_UTM_server.v1.netmanager.interface.update(UG_UTM_auth_token, node_name_1, line_in_dict_bonds, {"enabled": False})
                if result_1_1:
                    logger.success(f"Interface {line_in_dict_bonds} successfully deployed and disabled on node {disp_node_name_1}")
                else:
                    logger.error(f"Interface {line_in_dict_bonds} deployed on node {disp_node_name_1}, but not disabled, error: {result_1_1}")
            else:
                logger.error(f"Interface {line_in_dict_bonds} not deployed on node {disp_node_name_1}, error: {result_1}")
        except Exception as error:
            result_1 = result_1_1 = ''
            logger.error(f"Interface {line_in_dict_bonds} not deployed on node {disp_node_name_1}, error: {type(error).__name__} - {error}")

        # Deploy bond on node 2
        try:
            result_2 = UG_UTM_server.v1.netmanager.interface.add.bond(UG_UTM_auth_token, node_name_2, line_in_dict_bonds, interface_details_2)
            if result_2 == line_in_dict_bonds:
                result_2_2 = UG_UTM_server.v1.netmanager.interface.update(UG_UTM_auth_token, node_name_2, line_in_dict_bonds, {"enabled": False})
                if result_2_2:
                    logger.success(f"Interface {line_in_dict_bonds} successfully deployed and disabled on node {disp_node_name_2}")
                else:
                    logger.error(f"Interface {line_in_dict_bonds} deployed on node {disp_node_name_2}, but not disabled, error: {result_1_1}")
            else:
                logger.error(f"Interface {line_in_dict_bonds} not deployed on node {disp_node_name_2}, error: {result_2}")
        except Exception as error:
            result_2 = result_2_2 = ''
            logger.error(f"Interface {line_in_dict_bonds} not deployed on node {disp_node_name_2}, error: {type(error).__name__} - {error}")

        # Deploy IP address of bond on Cluster
        if cluster_interface and result_1 == result_2 == line_in_dict_bonds:
            try:
                result_0_fetch = UG_UTM_server.v1.ha.cluster.fetch(UG_UTM_auth_token, cluster_id)
                existing_cluster_addresses = result_0_fetch['virtual_ips']
                existing_cluster_addresses.append(cluster_interface)
                update_cluster = {
                    'virtual_ips': existing_cluster_addresses
                }
                result_0_update = UG_UTM_server.v1.ha.cluster.update(UG_UTM_auth_token, cluster_id, update_cluster)
                if result_0_update:
                    logger.success(f"Cluster address {dict_bonds[line_in_dict_bonds]['0_ip_ug']} was successfully added to the interface {line_in_dict_bonds}")
                else:
                    logger.error(f"Cluster address {dict_bonds[line_in_dict_bonds]['0_ip_ug']} not deployed to the interface {line_in_dict_bonds}")
                
            except Exception as error:
                logger.error(f"Cluster address {dict_bonds[line_in_dict_bonds]['0_ip_ug']} not deployed to the interface {line_in_dict_bonds}, error: {type(error).__name__} - {error}")

#----------------------------------------------------------------------------------------------
# Check Point
stop = input("Continue program execution?\n1 Yes\n2 No\n")
if stop == '2' or stop.lower() == 'no' or stop == '':
    try:
        UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
        logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
    except:
        logger.error(f"Trouble with release token")
    quit()

#----------------------------------------------------------------------------------------------
# 2. Deploy main physical interfaces
logger.info("Searching main physical interfaces")

# Find all main physical interface
dict_physical = {}
for line_in_dict_plan in dict_ip_plan:
    if (line_in_dict_plan['physical'][0:4] == line_in_dict_plan['logical'][0:4] == 'port' and
        line_in_dict_plan['physical'].find('.') == -1):
        dict_physical[line_in_dict_plan['physical']] = {
            "0_ip_ug": "",
            "1_ip_ug": "",
            "2_ip_ug": "",
            "mask": "",
            "zone": 0
            }

# Fill dictionary with main physical interface
pop_numbers = []
for line_in_dict_physical in dict_physical:
    for count, line_in_dict_plan in enumerate(dict_ip_plan):

        if line_in_dict_physical == line_in_dict_plan['logical'] == line_in_dict_plan['physical']:

            # Fill zone
            if line_in_dict_plan["zone"]:
                dict_physical[line_in_dict_physical]["zone"] = dict_zones_id[line_in_dict_plan["zone"]]

            # Fill IP
            if line_in_dict_plan["0_ip_ug"] or line_in_dict_plan["1_ip_ug"] or line_in_dict_plan["2_ip_ug"] or line_in_dict_plan["mask"]:

                # Not entered 0 IP
                while not line_in_dict_plan["0_ip_ug"]:
                    line_in_dict_plan["0_ip_ug"] = input(f"0 IP address not entered in the line number {count}, enter the correct address: ")

                # Not entered 1 IP
                while not line_in_dict_plan["1_ip_ug"]:
                    line_in_dict_plan["1_ip_ug"] = input(f"1 IP address not entered in the line number {count}, enter the correct address: ")

                # Not entered 2 IP
                while not line_in_dict_plan["2_ip_ug"]:
                    line_in_dict_plan["2_ip_ug"] = input(f"2 IP address not entered in the line number {count}, enter the correct address: ")

                # Not entered mask
                while not line_in_dict_plan["mask"]:
                    line_in_dict_plan["mask"] = input(f"IP mask not entered in the line number {count}, enter the correct mask: ")

                dict_physical[line_in_dict_physical]["0_ip_ug"], dict_physical[line_in_dict_physical]["mask"] = check_ip(count, line_in_dict_plan["0_ip_ug"], line_in_dict_plan["mask"])
                dict_physical[line_in_dict_physical]["1_ip_ug"], dict_physical[line_in_dict_physical]["mask"] = check_ip(count, line_in_dict_plan["1_ip_ug"], line_in_dict_plan["mask"])
                dict_physical[line_in_dict_physical]["2_ip_ug"], dict_physical[line_in_dict_physical]["mask"] = check_ip(count, line_in_dict_plan["2_ip_ug"], line_in_dict_plan["mask"])

                if not dict_physical[line_in_dict_physical]['zone']:
                    logger.warning(f"Zone not set for L3 interface {line_in_dict_physical}")

            pop_numbers.append(count)

# Cleaning ip_plan_selected
count = 0
for one_pop_numbers in pop_numbers:
    dict_ip_plan.pop(one_pop_numbers-count)
    count += 1

# Deploy physical interfaces
if dict_physical:
    logger.info(f"Main Physical Interfaces detected, deploy")
    for line_in_dict_physical in dict_physical:
        
        cluster_interface = {}
        interface_details_1 = {}
        interface_details_2 = {}

        # General info
        interface_details = {
            "name": line_in_dict_physical,
            "enabled": False,
            # "description": f'enabled:{(True if i["state"] == "on" else False)}',
            "zone_id": dict_physical[line_in_dict_physical]["zone"],
            }

        # IP info
        if dict_physical[line_in_dict_physical]["0_ip_ug"] or dict_physical[line_in_dict_physical]["1_ip_ug"] or dict_physical[line_in_dict_physical]["2_ip_ug"] or dict_physical[line_in_dict_physical]["mask"]:
            interface_details["mode"] = "static"

            interface_details_1 = interface_details.copy()
            interface_details_2 = interface_details.copy()

            cluster_interface = {'interfaces': 
                [{'ifname': line_in_dict_physical, 'node_name': node_name_1},
                 {'ifname': line_in_dict_physical, 'node_name': node_name_2}],
                 'ipv4': ipaddress.IPv4Interface(f'{dict_physical[line_in_dict_physical]["0_ip_ug"]}/{dict_physical[line_in_dict_physical]["mask"]}').with_prefixlen }

            interface_details_1["ipv4"] = [ipaddress.IPv4Interface(f'{dict_physical[line_in_dict_physical]["1_ip_ug"]}/{dict_physical[line_in_dict_physical]["mask"]}').with_prefixlen]
            interface_details_2["ipv4"] = [ipaddress.IPv4Interface(f'{dict_physical[line_in_dict_physical]["2_ip_ug"]}/{dict_physical[line_in_dict_physical]["mask"]}').with_prefixlen]

            logger.info(f'A config for the interface {line_in_dict_physical} with an IP address (vip: {dict_physical[line_in_dict_physical]["0_ip_ug"]}, node_1: {dict_physical[line_in_dict_physical]["1_ip_ug"]}, node_2: {dict_physical[line_in_dict_physical]["2_ip_ug"]}, mask: {dict_physical[line_in_dict_physical]["mask"]}) was been generated')

        else:
            interface_details["mode"] = "manual"

            interface_details_1 = interface_details.copy()
            interface_details_2 = interface_details.copy()

            logger.info(f"A config for the interface {line_in_dict_physical} without an IP address has been generated")

        # Deploy physical on node 1
        try:
            result_1 = UG_UTM_server.v1.netmanager.interface.update(UG_UTM_auth_token, node_name_1, line_in_dict_physical, interface_details_1)
            if result_1:
                result_1_1 = UG_UTM_server.v1.netmanager.interface.update(UG_UTM_auth_token, node_name_1, line_in_dict_physical, {"enabled": False})
                if result_1_1:
                    logger.success(f"Interface {line_in_dict_physical} successfully deployed and disabled on node {disp_node_name_1}")
                else:
                    logger.error(f"Interface {line_in_dict_physical} deployed on node {disp_node_name_1}, but not disabled, error: {result_1_1}")
            else:
                logger.error(f"Interface {line_in_dict_physical} not deployed on node {disp_node_name_1}, error: {result_1}")
        except Exception as error:
            result_1 = result_1_1 = False
            logger.error(f"Interface {line_in_dict_physical} not deployed on node {disp_node_name_1}, error: {type(error).__name__} - {error}")

        # Deploy physical on node 2
        try:
            result_2 = UG_UTM_server.v1.netmanager.interface.update(UG_UTM_auth_token, node_name_2, line_in_dict_physical, interface_details_2)
            if result_2:
                result_2_2 = UG_UTM_server.v1.netmanager.interface.update(UG_UTM_auth_token, node_name_2, line_in_dict_physical, {"enabled": False})
                if result_2_2:
                    logger.success(f"Interface {line_in_dict_physical} successfully deployed and disabled on node {disp_node_name_2}")
                else:
                    logger.error(f"Interface {line_in_dict_physical} deployed on node {disp_node_name_2}, but not disabled, error: {result_1_1}")
            else:
                logger.error(f"Interface {line_in_dict_physical} not deployed on node {disp_node_name_2}, error: {result_2}")
        except Exception as error:
            result_2 = result_2_2 = False
            logger.error(f"Interface {line_in_dict_physical} not deployed on node {disp_node_name_2}, error: {type(error).__name__} - {error}")

        # Deploy IP address of physical interface on Cluster
        if cluster_interface and result_1 and result_1_1 and result_2 and result_2_2:
            try:
                result_0_fetch = UG_UTM_server.v1.ha.cluster.fetch(UG_UTM_auth_token, cluster_id)
                existing_cluster_addresses = result_0_fetch['virtual_ips']
                existing_cluster_addresses.append(cluster_interface)
                update_cluster = {
                    'virtual_ips': existing_cluster_addresses
                }
                result_0_update = UG_UTM_server.v1.ha.cluster.update(UG_UTM_auth_token, cluster_id, update_cluster)
                if result_0_update:
                    logger.success(f"Cluster address {dict_physical[line_in_dict_physical]['0_ip_ug']} was successfully added to the interface {line_in_dict_physical}")
                else:
                    logger.error(f"Cluster address {dict_physical[line_in_dict_physical]['0_ip_ug']} not deployed to the interface {line_in_dict_physical}")
                
            except Exception as error:
                logger.error(f"Cluster address {dict_physical[line_in_dict_physical]['0_ip_ug']} not deployed to the interface {line_in_dict_physical}, error: {type(error).__name__} - {error}")

#----------------------------------------------------------------------------------------------
# Check Point
stop = input("Continue program execution?\n1 Yes\n2 No\n")
if stop == '2' or stop.lower() == 'no' or stop == '':
    try:
        UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
        logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
    except:
        logger.error(f"Trouble with release token")
    quit()

#-----------------------------------------------------------------------------------------------------------------------------------
# 3. Deploy Sub interface (VLAN)
logger.info(f"Deploy Sub Interfaces")
for count, line_in_dict_plan in enumerate(dict_ip_plan):

    if f'{line_in_dict_plan["physical"]}.' in line_in_dict_plan['logical']:

        cluster_interface = {}
        interface_details_1 = {}
        interface_details_2 = {}

        # General info
        part_of_name = line_in_dict_plan["logical"].split(".")
        interface_details = {
            "name": line_in_dict_plan["logical"],
            "enabled": False,
            #"description": f'enabled:{(True if i["state"] == "on" else False)}',
            "zone_id": dict_zones_id[line_in_dict_plan["zone"]],
            "link": part_of_name[0],
            "vlan_id": part_of_name[1]
        }

        # Fill IP
        if line_in_dict_plan["0_ip_ug"] or line_in_dict_plan["1_ip_ug"] or line_in_dict_plan["2_ip_ug"] or line_in_dict_plan["mask"]:

            # Not entered 0 IP
            while not line_in_dict_plan["0_ip_ug"]:
                line_in_dict_plan["0_ip_ug"] = input(f"0 IP address not entered in the line number {count}, enter the correct address: ")

            # Not entered 1 IP
            while not line_in_dict_plan["1_ip_ug"]:
                line_in_dict_plan["1_ip_ug"] = input(f"1 IP address not entered in the line number {count}, enter the correct address: ")

            # Not entered 2 IP
            while not line_in_dict_plan["2_ip_ug"]:
                line_in_dict_plan["2_ip_ug"] = input(f"2 IP address not entered in the line number {count}, enter the correct address: ")

            # Not entered mask
            while not line_in_dict_plan["mask"]:
                line_in_dict_plan["mask"] = input(f"IP mask not entered in the line number {count}, enter the correct mask: ")

            line_in_dict_plan["0_ip_ug"], line_in_dict_plan["mask"] = check_ip(count, line_in_dict_plan["0_ip_ug"], line_in_dict_plan["mask"])
            line_in_dict_plan["1_ip_ug"], line_in_dict_plan["mask"] = check_ip(count, line_in_dict_plan["1_ip_ug"], line_in_dict_plan["mask"])
            line_in_dict_plan["2_ip_ug"], line_in_dict_plan["mask"] = check_ip(count, line_in_dict_plan["2_ip_ug"], line_in_dict_plan["mask"])

            interface_details["mode"] = "static"

            cluster_interface = {'interfaces': 
                [{'ifname': line_in_dict_plan["logical"], 'node_name': node_name_1},
                 {'ifname': line_in_dict_plan["logical"], 'node_name': node_name_2}],
                 'ipv4': ipaddress.IPv4Interface(f'{line_in_dict_plan["0_ip_ug"]}/{line_in_dict_plan["mask"]}').with_prefixlen }

            interface_details_1 = interface_details.copy()
            interface_details_2 = interface_details.copy()

            interface_details_1["ipv4"] = [ipaddress.IPv4Interface(f'{line_in_dict_plan["1_ip_ug"]}/{line_in_dict_plan["mask"]}').with_prefixlen]
            interface_details_2["ipv4"] = [ipaddress.IPv4Interface(f'{line_in_dict_plan["2_ip_ug"]}/{line_in_dict_plan["mask"]}').with_prefixlen]

            logger.info(f'A config for the interface {line_in_dict_plan["logical"]} with an IP address (vip: {line_in_dict_plan["0_ip_ug"]}, node_1: {line_in_dict_plan["1_ip_ug"]}, node_2: {line_in_dict_plan["2_ip_ug"]}, mask: {line_in_dict_plan["mask"]}) was been generated')

        else:
            interface_details["mode"] = "manual"

            interface_details_1 = interface_details.copy()
            interface_details_2 = interface_details.copy()

            logger.warning(f"A config for the interface {line_in_dict_plan['logical']} without an IP address has been generated")

        # Deploy Sub interface on node 1
        try:
            result_1 = UG_UTM_server.v1.netmanager.interface.add.vlan(UG_UTM_auth_token, node_name_1, line_in_dict_plan["logical"], interface_details_1)
            if result_1:
                logger.success(f"Interface {line_in_dict_plan['logical']} successfully deployed on node {disp_node_name_1}")
            else:
                logger.error(f"Interface {line_in_dict_plan['logical']} not deployed on node {disp_node_name_1}, error: {result_1}")
        except Exception as error:
            result_1 = False
            logger.error(f"Interface {line_in_dict_plan['logical']} not deployed on node {disp_node_name_1}, error: {type(error).__name__} - {error}")

        # Deploy Sub interface on node 2
        try:
            result_2 = UG_UTM_server.v1.netmanager.interface.add.vlan(UG_UTM_auth_token, node_name_2, line_in_dict_plan["logical"], interface_details_2)
            if result_2:
                logger.success(f"Interface {line_in_dict_plan['logical']} successfully deployed on node {disp_node_name_2}")
            else:
                logger.error(f"Interface {line_in_dict_plan['logical']} not deployed on node {disp_node_name_2}, error: {result_2}")
        except Exception as error:
            result_2 = False
            logger.error(f"Interface {line_in_dict_plan['logical']} not deployed on node {disp_node_name_2}, error: {type(error).__name__} - {error}")

        # Deploy IP address of physical interface on Cluster
        if cluster_interface and result_1 and result_2:
            try:
                result_0_fetch = UG_UTM_server.v1.ha.cluster.fetch(UG_UTM_auth_token, cluster_id)
                existing_cluster_addresses = result_0_fetch['virtual_ips']
                existing_cluster_addresses.append(cluster_interface)
                update_cluster = {
                    'virtual_ips': existing_cluster_addresses
                }
                result_0_update = UG_UTM_server.v1.ha.cluster.update(UG_UTM_auth_token, cluster_id, update_cluster)
                if result_0_update:
                    logger.success(f"Cluster address {line_in_dict_plan['0_ip_ug']} was successfully added to the interface {line_in_dict_plan['logical']}")
                    #logger.success(f"Cluster address was successfully added to the interface {line_in_dict_plan['logical']}")
                else:
                    logger.error(f"Cluster address {line_in_dict_plan['0_ip_ug']} not deployed to the interface {line_in_dict_plan['logical']}")
                    #logger.error(f"Cluster address not deployed to the interface {line_in_dict_plan['logical']}")
                
            except Exception as error:
                logger.error(f"Cluster address {line_in_dict_plan['0_ip_ug']} not deployed to the interface {line_in_dict_plan['logical']}, error: {type(error).__name__} - {error}")
                #logger.error(f"Cluster address not deployed to the interface {line_in_dict_plan['logical']}, error: {type(error).__name__} - {error}")

# Realese token

try:
    UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
    logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
except:
    logger.error(f"Trouble with release token")