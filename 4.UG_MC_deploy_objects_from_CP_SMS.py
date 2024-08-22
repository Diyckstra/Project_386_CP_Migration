from functions import *
from functions_UG import UG_get_token, UG_release_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_4}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
logger.info(f"Script starts")

# Open UG MC cred file
try:
    with open(f"{path['input_path']}/{UG_MC_creds_file}") as file:
        R_UG_MC = json.load(file)
    logger.info(f"File {path['input_path']}/{UG_MC_creds_file} opened")
# File not found
except FileNotFoundError:
    logger.error(f"File {path['input_path']}/{UG_MC_creds_file} not found")
    quit()

# Read UG MC cred file
try:
    UG_MC_fw_address   = R_UG_MC["address"]
    UG_MC_fw_api_port  = R_UG_MC["port"]
    UG_MC_user         = R_UG_MC["user"]
    UG_MC_password     = R_UG_MC["password"]
    logger.info(f"File {path['input_path']}/{UG_MC_creds_file} is filled in correctly")
except KeyError:
    logger.error(f"File {path['input_path']}/{UG_MC_creds_file} is filled in incorrectly")

# Get auth token
UG_MC_server, UG_MC_auth_token = UG_get_token(UG_MC_fw_address, UG_MC_fw_api_port, UG_MC_user, UG_MC_password)
if UG_MC_auth_token:
    logger.success("Token received")
else:
    logger.error(f"Token not received, error: {UG_MC_server}")
    quit()

# ------------ H O S T S - N E T W O R K S - A D D R E S S - R A N G E S - C P - H O S T S ------------------------------------------------
logger.info(f"Deploy objects hosts, networks, address-ranges and Check Point Hosts")
groups_objects = {}

# Open objects file
try:
    with open(f"{path['sms_config_path']}/Objects.json") as file:
        OBJECTS = json.load(file)
    logger.info(f"File {path['sms_config_path']}/Objects.json opened")
# File not found
except FileNotFoundError:
    logger.error(f"File {path['sms_config_path']}/Objects.json not found")
    quit()

SIMPLE_OBJECTS = (OBJECTS["hosts"]["items"] 
                  + OBJECTS["networks"]["items"] 
                  + OBJECTS["address-ranges"]["items"] 
                  + OBJECTS["checkpoint-hosts"]["items"] 
                  + OBJECTS["simple-clusters"]["items"])

for net_list in SIMPLE_OBJECTS:

    # Exclude network with only ipv6
    if net_list["type"] == "network":
        try:
            net_list["subnet6"]
            continue
        except:
            None

    # deploy list
    try:
        response_add_list = UG_MC_server.v1.ccnlists.list.add(UG_MC_auth_token, UG_MC_template_objects["id"], {
            "name": net_list["name"],
            "description": net_list["comments"],
            "type": "network"
        })
        # fill list
        if len(response_add_list) == 36:
            logger.success(f"Object {net_list['name']} created")
            net_address = ""

            # with host
            if net_list["type"] == "host":
                net_address = net_list["ipv4-address"]

                # Cashe group objects
                for member in net_list["groups"]:
                    try:
                        groups_objects[member].append(net_address)
                    except :
                        groups_objects[member] = []
                        groups_objects[member].append(net_address)

            # with network
            elif net_list["type"] == "network":
                net_address = f'{net_list["subnet4"]}/{net_list["mask-length4"]}'

                # Cashe group objects
                for member in net_list["groups"]:
                    try:
                        groups_objects[member].append(net_address)
                    except:
                        groups_objects[member] = []
                        groups_objects[member].append(net_address)
            
            # with address-ranges
            elif net_list["type"] == "address-range":
                net_address = f'{net_list["ipv4-address-first"]}-{net_list["ipv4-address-last"]}'
            
            # with checkpoint-host or simple-cluster
            elif net_list["type"] == "checkpoint-host" or net_list["type"] == "simple-cluster":
                net_address = net_list["ipv4-address"]

            else:
                logger.error(f"For object <{net_list['name']}> unknown type: {net_list['type']}")
                continue

            # fiiiiiiiiil
            response_add_item_to_list = UG_MC_server.v1.ccnlists.item.add(UG_MC_auth_token, UG_MC_template_objects["id"], response_add_list, {
                "list": "network",
                "value": net_address
            })
            if len(response_add_item_to_list) == 36:
                logger.success(f"Object {net_list['name']} filled")
            else:
                logger.error(f"Object {net_list['name']} not filled")
        else:
            logger.error(f"Object {net_list['name']} not created")
    except Exception as error:
        logger.error(f"Object {net_list['name']} not created, error: {error}")


# ------------ G R O U P S ------------------------------------------------
logger.info(f"Deploy Group Objects")
for member_in_group in groups_objects:
    # deploy list
    try:
        response_add_list = UG_MC_server.v1.ccnlists.list.add(UG_MC_auth_token, UG_MC_template_objects["id"], {
            "name": member_in_group,
            "type": "network"
        })
        # fill list
        if len(response_add_list) == 36:
            logger.success(f"Object {member_in_group} created")
            net_address = []
            for member_group_in_cashe in groups_objects[member_in_group]:
                net_address.append({
                    "list": "network",
                    "value": member_group_in_cashe
                })
            # fiiiiiiiiil
            response_add_items_to_list = UG_MC_server.v1.ccnlists.items.add(UG_MC_auth_token, UG_MC_template_objects["id"], response_add_list, net_address)
            if len(groups_objects[member_in_group]) == response_add_items_to_list:
                logger.success(f"Object {member_in_group} filled")
            else:
                logger.error(f"Object {member_in_group} not filled")
        else:
            logger.error(f"Object {member_in_group} not created")
    except:
        logger.error(f"Object {member_in_group} not created")

# Release token
release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
if not release_token:
    logger.success("Token released")
else:
    logger.error("Token not released")
