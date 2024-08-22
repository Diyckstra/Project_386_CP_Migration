from functions import *
from functions_UG import UG_UTM_get_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_10}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
logger.info(f"Script starts")


files = os.listdir(path['input_path'])
cfg_files = []

for file in files:
    if file[-4:] == '.cfg':
        cfg_files.append(file)

wrong_attempt = 0

# Enter node number
print("\n#---------N O D E - N U M B E R-------------#\n")
while True:
    node_number = input(f"For cluster <{UG_UTM_selected_creds_file}> enter node number (1 or 2): ")
    if node_number.isdigit():
        if 0 < int(node_number) < 3:
            break
        else:
            wrong_attempt += 1
            print(f"The amount of your stupidity: {wrong_attempt}\n")
    else:
        wrong_attempt += 1
        print(f"The amount of your stupidity: {wrong_attempt}\n")
node_number = int(node_number)

# Enter policy
print("\n#---------C O N F I G-------------#\n")
while True:
    print(f"In directory <{path['input_path']}> found configs:")
    for count, conf in enumerate(cfg_files):
        print(f"{count} {conf}")

    number_policy = input(f"For cluster <{UG_UTM_selected_creds_file}> node number <{node_number}> enter config number: ")

    if number_policy.isdigit():
        if -1 < int(number_policy) < len(cfg_files):
            break
        else:
            wrong_attempt += 1
            print(f"The amount of your stupidity: {wrong_attempt}\n")
    else:
        wrong_attempt += 1
        print(f"The amount of your stupidity: {wrong_attempt}\n")
target_config = cfg_files[int(number_policy)]

#--------------P A R S I N G--------------------------------------------------------------------------------------------------
# Open config file
try:
    with open(f"{path['input_path']}/{target_config}") as file:
        config = file.read().splitlines()
    logger.info(f"File {path['input_path']}/{target_config} opened")
# File not found
except FileNotFoundError:
    logger.error(f"File {path['input_path']}/{target_config} not found")
    quit()
except Exception as error:
    logger.error(f"File {path['input_path']}/{target_config} not opend, error: {error}")

logger.info(f"Read routes in file {path['input_path']}/{target_config}")

snmp_block = []
arp_block = []
interface_block = []
static_route_block = []
pbr_block = []
other_block = []

for line_config in config:
    if line_config:
        
        # Comment && empty lines
        if line_config[0] == '#' or line_config[0] == ' ':
            None

        # SNMP
        elif line_config.find("set snmp ") != -1:
            snmp_block.append(line_config)

        # ARP
        elif line_config.find("add arp proxy ") != -1:
            arp_block.append(line_config)

        # PBR
        elif line_config.find("set pbr ") != -1:
            pbr_block.append(line_config)

        # Static Route
        elif line_config.find("set static-route ") != -1:
            static_route_block.append(line_config)

        # Interface
        elif ((line_config.find("add interface ") != -1) or 
              (line_config.find("set interface ") != -1) or 
              (line_config.find("set pim interface ") != -1) or 
              (line_config.find("set bonding group ") != -1) or
              (line_config.find("add bonding group ") != -1) or
              (line_config.find("set igmp interface ") != -1)):
            interface_block.append(line_config)

        # Other
        else:
            other_block.append(line_config)


#--------------F I L T E R - A R P - P R O X Y--------------------------------------------------------------------------------------------------
arp_dictionary = []
# add arp proxy ipv4-address 195.128.70.7 interface eth3.441 real-ipv4-address 195.128.70.252
for arp_line in arp_block:
    if ('add arp proxy ipv4-address ' in arp_line and 
        ' interface ' in arp_line and
        'ipv4-address ' in arp_line):
        tmp_record = arp_line.split(' ')
        arp_dictionary.append(
            {
                'arp_ip': tmp_record[4],
                'iface': tmp_record[6],
                'real_ip': tmp_record[8]
            }
        )

pprint(arp_dictionary)


# #--------------F I L T E R - R O U T E S--------------------------------------------------------------------------------------------------
# logger.info(f"Parsing routes in file {path['input_path']}/{target_config}")
# routes = {}
# for route_line in static_route_block:
#     tmp_route = route_line.split(' ')

#     # Address
#     if tmp_route[3] == 'nexthop' and tmp_route[4] == 'gateway':
#         try:
#             routes[tmp_route[2]][tmp_route[4]] = tmp_route[6]
#             routes[tmp_route[2]]["state"] = tmp_route[7]
#             routes[tmp_route[2]]["destination"] = tmp_route[2]
#             routes[tmp_route[2]]["type"] = tmp_route[5]

#         except KeyError:
#             routes[tmp_route[2]] = {}
#             routes[tmp_route[2]][tmp_route[4]] = tmp_route[6]
#             routes[tmp_route[2]]["state"] = tmp_route[7]
#             routes[tmp_route[2]]["destination"] = tmp_route[2]
#             routes[tmp_route[2]]["type"] = tmp_route[5]

#     # comment
#     elif tmp_route[3] == 'comment':
#         try:
#             routes[tmp_route[2]][tmp_route[3]] = route_line.split('comment')[1].replace('\"', '')

#         except KeyError:
#             routes[tmp_route[2]] = {}
#             routes[tmp_route[2]][tmp_route[3]] = route_line.split('comment')[1].replace('\"', '')

#     else:
#         logger.warning(f"Trouble with route <{route_line}>")
#         print(route_line)

# parsed_routes = []
# for route in routes:

#     if route == "default":
#         logger.warning(f"The default route will not be deployed for security reasons")
#         continue

#     # comment
#     try:
#         routes[route]['comment'] = routes[route]['comment'].replace("\"", "")
#     except KeyError:
#         routes[route]['comment'] = ''

#     # route
#     try:
#         routes[route]['destination']
#         routes[route]['gateway']
#         routes[route]['state']
#         routes[route]['type']

#         parsed_routes.append(routes[route])
#         logger.info(f"Route <{route}> read correctly")
        

#     except KeyError:
#         logger.warning(f"Trouble with route <{route}>")

# #--------------C O N N E C T I N G - T O - M C--------------------------------------------------------------------------------------------------

# # Get creds to UG UTM
# try:
#     with open(f"{path['input_path']}/{UG_UTM_selected_creds_file}") as file:
#         R_UG_UTM = json.load(file)
#     UG_UTM_fw_address   = R_UG_UTM["address"]
#     UG_UTM_fw_api_port  = R_UG_UTM["port"]
#     UG_UTM_user         = R_UG_UTM["user"]
#     UG_UTM_password     = R_UG_UTM["password"]

#     logger.info(f"Creds file {path['input_path']}/{UG_UTM_selected_creds_file} read")

# # Credentials file not found
# except FileNotFoundError:
#     logger.error(f"Creds file {path['input_path']}/{UG_UTM_selected_creds_file} not found. Program exit")
#     quit()

# # No node is available
# except BlockingIOError:
#     logger.error(f"UG UTM {UG_UTM_fw_address} is unavailable. Program exit")
#     quit()

# # Get auth token
# UG_UTM_server, UG_UTM_auth_token = UG_UTM_get_token(UG_UTM_fw_address, UG_UTM_fw_api_port, UG_UTM_user, UG_UTM_password)
# if UG_UTM_auth_token:
#     logger.success(f"Authorization token received from UG UTM {UG_UTM_fw_address}")
# else:
#     logger.error(f"Token not received, error: {UG_UTM_server}")
#     quit()

# try:
#     node_name = UG_UTM_server.v2.core.nodes.list(UG_UTM_auth_token)

#     # Both nodes are available
#     if node_name[0]['status'] == 'online' and node_name[1]['status'] == 'online':
#         logger.info(f"Both nodes are available")

#         if node_name[0]['license'] == 'active' and node_name[1]['license'] == 'active':
#             logger.info(f"Both nodes are activated")

#     # First node available
#     elif node_name[0]['status'] != 'online':
#         logger.error(f"{node_name[0]['cc_node_name']} <{node_name[0]['name']}> <{node_name[0]['display_name']}> is {node_name[0]['status']}. Program exit")
#         try:
#             UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
#             logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
#         except:
#             logger.error(f"Trouble with release token")
#         quit()

#     # Second node is available
#     elif node_name[1]['status'] != 'online':
#         logger.error(f"{node_name[1]['cc_node_name']} <{node_name[1]['name']}> <{node_name[1]['display_name']}> is {node_name[1]['status']}. Program exit")
#         try:
#             UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
#             logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
#         except:
#             logger.error(f"Trouble with release token")
#         quit()

#     # Verify node names
#     if node_name[0]['cc_node_name'] == "node_1" and node_name[1]['cc_node_name'] == "node_2":
#         node_name_1 = node_name[0]['name']
#         node_name_2 = node_name[1]['name']
#         disp_node_name_1 = node_name[0]['display_name']
#         disp_node_name_2 = node_name[1]['display_name']
#         logger.info(f"Node names are defined: {node_name_1} ({disp_node_name_1}) and {node_name_2} ({disp_node_name_2})")

#     elif node_name[1]['cc_node_name'] == "node_1" and node_name[0]['cc_node_name'] == "node_2":
#         node_name_1 = node_name[1]['name']
#         node_name_2 = node_name[0]['name']
#         disp_node_name_1 = node_name[1]['display_name']
#         disp_node_name_2 = node_name[0]['display_name']
#         logger.info(f"Node names are defined: {node_name_1} ({disp_node_name_1}) and {node_name_2} ({disp_node_name_2})")
#     else:
#         logger.error(f"There is some problem with determining the names of the nodes. Program exit")
#         quit()

#     result_cluster_list = UG_UTM_server.v1.ha.clusters.list(UG_UTM_auth_token)
#     if len(result_cluster_list) > 1:
#         logger.error(f"More than one cluster detected")
#         try:
#             UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
#             logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
#         except:
#             logger.error(f"Trouble with release token")
#         quit()
#     else:
#         logger.success(f"One cluster detected: {result_cluster_list[0]['name']}")
#         cluster_id = result_cluster_list[0]["id"]

# # Credentials file not found
# except FileNotFoundError:
#     logger.error(f"Creds file {path['input_path']}/{UG_UTM_selected_creds_file} not found. Program exit")
#     quit()

# # No node is available
# except BlockingIOError:
#     logger.error(f"UG UTM {UG_UTM_fw_address} is unavailable. Program exit")
#     quit()

# if node_number == 1:
#     node_name_selected = node_name_1
#     disp_node_name_selected = disp_node_name_1
# elif node_number == 2:
#     node_name_selected = node_name_2
#     disp_node_name_selected = disp_node_name_2

# logger.info(f"Deploying routes to <{node_name_selected}> <{disp_node_name_selected}>")

# # Check Point
# stop = input("Continue program execution?\n1 Yes\n2 No\n")
# if stop == '2' or stop.lower() == 'no' or stop == '':
#     try:
#         UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
#         logger.success(f"Authorization token released from UG UTM {UG_UTM_fw_address}")
#     except:
#         logger.error(f"Trouble with release token")
#     quit()



# #--------------D E P L O Y - R O U T E S--------------------------------------------------------------------------------------------------

# # Get router info
# router = {}
# try:
#     response = UG_UTM_server.v1.netmanager.virtualrouters.list(UG_UTM_auth_token)
#     for i in response:
#         if i['node_name'] == node_name_selected:
#             router = i
#             logger.info(f"Information received about router from UTM <{node_name_selected}> <{disp_node_name_selected}>")
#             break
#             # pprint(i)
# except Exception as error:
#     logger.error(f"Information not received about router from UTM <{node_name_selected}> <{disp_node_name_selected}>")
#     quit()

# # Formation of a route list
# for route in parsed_routes:
#     if route["type"] == "address":
#         tmp_route = {
#             "name": route["destination"],
#             "description": route["comment"],
#             "enabled": (True if route["state"] == "on" else False),
#             "dest": route["destination"],
#             "gateway": route["gateway"]
#         }
#         router['routes'].append(tmp_route)

# # Deploy routes
# try:
#     update_router_response = UG_UTM_server.v1.netmanager.virtualrouter.update(  #String auth_token, String id, VirtualRouterInfo router
#         UG_UTM_auth_token,
#         f"{node_name_selected}:default",
#         router
#         )
#     if update_router_response:
#         logger.success(f"Routes deployed to UTM <{node_name_selected}> <{disp_node_name_selected}>")
#     else:
#         logger.error(f"Routes not deployed to UTM <{node_name_selected}> <{disp_node_name_selected}>")
# except Exception as error:
#     logger.error(f"Routes not deployed to UTM <{node_name_selected}> <{disp_node_name_selected}>")
#     quit()



# # {'bgp': {'as_number': 1,
# #          'enabled': False,
# #          'filters': [],
# #          'id': '',
# #          'multiple_path': False,
# #          'neighbors': [],
# #          'networks': [],
# #          'redistribute': [],
# #          'routemaps': [],
# #          'router_id': ''},
# #  'cc': False,
# #  'description': 'default',
# #  'id': 'utmcore@kintharedlet:default',
# #  'interfaces': [],
# #  'name': 'default',
# #  'node_name': 'utmcore@kintharedlet',
# #  'ospf': {'areas': [],
# #           'default_originate': False,
# #           'enabled': False,
# #           'id': '',
# #           'interfaces': [],
# #           'metric': '',
# #           'redistribute': [],
# #           'router_id': ''},
# #  'pimsm': {'ecmp_rebalance': False,
# #            'enabled': False,
# #            'id': '',
# #            'interfaces': [],
# #            'join_prune_interval': 60,
# #            'keep_alive_timer': 31,
# #            'register_suppress_time': 5,
# #            'rpmappings': [],
# #            'spt_exclusions': [],
# #            'ssm_address_range': [],
# #            'use_ecmp': False},
# #  'rip': {'administrative_distance': 1,
# #          'default_metric': 1,
# #          'default_originate': 1,
# #          'enabled': False,
# #          'id': '',
# #          'interfaces': [],
# #          'networks': [],
# #          'redistribute': [],
# #          'version': 1},
# #  'routes': []}




# # {'10.0.0.0/15': {'destination': '10.0.0.0/15',
# #                  'gateway': '10.163.46.254',
# #                  'state': 'on',
# #                  'type': 'address'},
# #  '10.10.101.0/24': {'destination': '10.10.101.0/24',
# #                     'gateway': '10.200.1.7',
# #                     'state': 'on',
# #                     'type': 'address'},
# #  '10.10.103.0/24': {'destination': '10.10.103.0/24',
# #                     'gateway': '10.200.1.7',
# #                     'state': 'on',
# #                     'type': 'address'},
# #  '10.10.144.0/24': {'destination': '10.10.144.0/24',
# #                     'gateway': '10.200.1.7',
# #                     'state': 'on',
# #                     'type': 'address'},
# #  '10.10.48.0/24': {'destination': '10.10.48.0/24',
# #                    'gateway': '10.200.1.7',
# #                    'state': 'on',
# #                    'type': 'address'},
# #  '10.11.2.0/24': {'comment': '"DMZ',
# #                   'destination': '10.11.2.0/24',
# #                   'gateway': '10.200.1.4',
# #                   'state': 'on',
# #                   'type': 'address'},
# #  '10.11.3.0/24': {'comment': '"DMZ',
# #                   'destination': '10.11.3.0/24',
# #                   'gateway': '10.200.1.4',
# #                   'state': 'on',
# #                   'type': 'address'},
# #  '10.112.0.0/14': {'comment': '"KSPD.',
# #                    'destination': '10.112.0.0/14',
# #                    'gateway': '10.163.46.254',
# #                    'state': 'on',
# #                    'type': 'address'},

# # Realese token
# try:
#     UG_UTM_server.v2.core.logout(UG_UTM_auth_token)
# except:
#     print("Trouble with release token")
