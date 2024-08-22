from functions import *
from functions_UG import UG_get_token, UG_release_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_5}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
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

# ------------ S E R V I C E S ------------------------------------------------
logger.info(f"Deploy services")
groups_services = {}
dict_service_uid = {}

# Open objects file
try:
    with open(f"{path['sms_config_path']}/Services.json") as file:
        OBJECTS = json.load(file)
    logger.info(f"File {path['sms_config_path']}/Services.json opened")
# File not found
except FileNotFoundError:
    logger.error(f"File {path['sms_config_path']}/Services.json not found")
    quit()

# Deploy ICMP
for service_list in OBJECTS["services-icmp"]["items"]:
    # Deploy service
    try:
        response_add_service = UG_MC_server.v1.ccnetwork.service.add(UG_MC_auth_token, UG_MC_template_objects["id"], 
                                                                    {
                                                                        "name": service_list["name"],
                                                                        "description": service_list["comments"],
                                                                        "protocols": [{"proto": "icmp"}]
                                                                    })
        if len(response_add_service) == 36:
            logger.success(f"Service {service_list['name']} created")

            # Cashe UID service
            dict_service_uid[service_list["name"]] = response_add_service

            # Cashe group services
            for member in service_list["groups"]:
                try:
                    groups_services[member]["description"].append(service_list["name"])
                    if {"proto": "icmp"} not in groups_services[member]["protocols"]:
                        groups_services[member]["protocols"].append({"proto": "icmp"})
                except:
                    groups_services[member] = {}
                    groups_services[member]["description"] = []
                    groups_services[member]["protocols"] = []
                    groups_services[member]["description"].append(service_list["name"])
                    groups_services[member]["protocols"].append({"proto": "icmp"})

        else:
            logger.error(f"Service {service_list['name']} not created")
    except Exception as error:
        logger.error(f"Service <{service_list['name']}> not created, error: {error}")


# Deploy simple services
SIMPLE_SERVICES = OBJECTS["services-udp"]["items"] + OBJECTS["services-tcp"]["items"]

for service_list in SIMPLE_SERVICES:

    # Miss strange for UG services
    if service_list["port"] == "Any":
        logger.warning(f"Service {service_list['name']} not created, because destination port = {service_list['port']}")
        continue

    # >1023, >0
    elif service_list["port"][0] == '>':
        tmp_port = int(service_list["port"][1:])
        service_list["port"] = f"{(tmp_port + 1 if tmp_port == 0 else tmp_port)}-65535"

    # Add destination port
    tmp_protocol = {
        "proto": ("udp" if service_list["type"] == "service-udp" else "tcp"),
        "port": service_list["port"]
        }

    # Add source port
    try:
        tmp_protocol = {
            "proto": ("udp" if service_list["type"] == "service-udp" else "tcp"),
            "port": service_list["port"],
            "source_port": service_list["source-port"]
            }
    except:
        tmp_protocol = {
            "proto": ("udp" if service_list["type"] == "service-udp" else "tcp"),
            "port": service_list["port"]
            }

    # Deploy service
    try:
        response_add_service = UG_MC_server.v1.ccnetwork.service.add(UG_MC_auth_token, UG_MC_template_objects["id"], 
                                                                     {
                                                                        "name": service_list["name"],
                                                                        "description": service_list["comments"],
                                                                        "protocols": [
                                                                            tmp_protocol
                                                                        ]
                                                                     })
        if len(response_add_service) == 36:
            logger.success(f"Service {service_list['name']} created")

            # Cashe UID service
            dict_service_uid[service_list["name"]] = response_add_service

            # Cashe group services
            for member in service_list["groups"]:
                try:
                    groups_services[member]["description"].append(service_list["name"])
                    groups_services[member]["protocols"].append(tmp_protocol)
                except:
                    groups_services[member] = {}
                    groups_services[member]["description"] = []
                    groups_services[member]["protocols"] = []
                    groups_services[member]["description"].append(service_list["name"])
                    groups_services[member]["protocols"].append(tmp_protocol)

        else:
            logger.error(f"Service {service_list['name']} not created")
    except Exception as error:
        logger.error(f"Service <{service_list['name']}> not created, error: {error}")


# ------------ S E R V I C E - G R O U P S ------------------------------------------------
logger.info(f"Deploy Service Group")
not_deployed_group_service = []

# First interation deploys
for imported_service_group in OBJECTS["service-groups"]["items"]:
    logger.debug(f"First check service-group <{imported_service_group['name']}>")
    try:
        if len(imported_service_group['members']) == len(groups_services[imported_service_group['name']]['description']):
            logger.success(f"For service-group <{imported_service_group['name']}> group members were previously created in full")

            # Cashe group services
            for member in imported_service_group["groups"]:
                try:
                    groups_services[member]["description"].append(service_list["name"])
                    tmp_group_protocol = groups_services[member]["protocols"] + groups_services[imported_service_group["name"]]["protocols"]
                    groups_services[member]["protocols"] = tmp_group_protocol
                except:
                    groups_services[member] = {}
                    groups_services[member]["description"] = []
                    groups_services[member]["protocols"] = []
                    groups_services[member]["description"].append(service_list["name"])
                    tmp_group_protocol = groups_services[member]["protocols"] + groups_services[imported_service_group["name"]]["protocols"]
                    groups_services[member]["protocols"] = tmp_group_protocol

            deploy_flag = True

        else:
            logger.info(f"At first iteration for service-group <{imported_service_group['name']}> not created members: {list(set(imported_service_group['members']) - set(groups_services[imported_service_group['name']]['description']))}")
            not_deployed_group_service.append(imported_service_group["name"])
            deploy_flag = False

    except KeyError:
        logger.info(f"For service-group <{imported_service_group['name']}> no group members have been created previously. Not deploying. Missing group members: {imported_service_group['members']}")
        not_deployed_group_service.append(imported_service_group["name"])
        deploy_flag = False

    if deploy_flag:
        try:
            logger.debug(f"Deploy service-group <{imported_service_group['name']}>")

            response_add_service = UG_MC_server.v1.ccnetwork.service.add(UG_MC_auth_token, UG_MC_template_objects["id"], 
                                                                                {
                                                                                    "name": imported_service_group['name'],
                                                                                    "description": f"group_of: {', '.join([str(elem) for elem in groups_services[imported_service_group['name']]['description']])}",
                                                                                    "protocols": groups_services[imported_service_group['name']]["protocols"]
                                                                                })

            if len(response_add_service) == 36:
                logger.success(f"Service-group {imported_service_group['name']} created")

                # Cashe UID service
                dict_service_uid[imported_service_group['name']] = response_add_service
            else:
                logger.error(f"Service-group {imported_service_group['name']} not created")
        except Exception as error:
            logger.error(f"Service-group <{imported_service_group['name']}> not created, error: {error}")

# Second iteration deploys
for imported_service_group in OBJECTS["service-groups"]["items"]:
    if imported_service_group["name"] in not_deployed_group_service:
        logger.debug(f"Second check service-group <{imported_service_group['name']}>")
        try:        
            if len(imported_service_group['members']) == len(groups_services[imported_service_group['name']]['description']):
                logger.success(f"For service-group <{imported_service_group['name']}> group members were previously created in full")
                deploy_flag = True

            else:
                logger.warning(f"For service-group <{imported_service_group['name']}> not created members: {list(set(imported_service_group['members']) - set(groups_services[imported_service_group['name']]['description']))}")
                not_deployed_group_service.append(imported_service_group["name"])
                deploy_flag = True

        except KeyError:
            logger.warning(f"For service-group <{imported_service_group['name']}> no group members have been created previously. Missing group members: {imported_service_group['members']}. Group not deployed.")
            deploy_flag = False

        if deploy_flag:
            try:
                logger.debug(f"Deploy service-group <{imported_service_group['name']}>")

                response_add_service = UG_MC_server.v1.ccnetwork.service.add(UG_MC_auth_token, UG_MC_template_objects["id"], 
                                                                                    {
                                                                                        "name": imported_service_group['name'],
                                                                                        "description": f"group_of: {', '.join([str(elem) for elem in groups_services[imported_service_group['name']]['description']])}",
                                                                                        "protocols": groups_services[imported_service_group['name']]["protocols"]
                                                                                    })

                if len(response_add_service) == 36:
                    logger.success(f"Service-group {imported_service_group['name']} created")

                    # Cashe UID service
                    dict_service_uid[imported_service_group['name']] = response_add_service
                else:
                    logger.error(f"Service-group {imported_service_group['name']} not created")
            except Exception as error:
                logger.error(f"Service-group <{imported_service_group['name']}> not created, error: {error}")

with open(f'{path["output_path"]}/Services_UID.json', 'w', encoding='utf-8') as f:
    json.dump(dict_service_uid, f, ensure_ascii=False, indent=4)

# Release token
release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
if not release_token:
    logger.success("Token released")
else:
    logger.error("Token not released")
