from functions import *
from functions_UG import UG_get_token, UG_release_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_2}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
logger.info(f"Script starts")

# Open file
dict_ip_plan = []
try:
    with open(f"{path['output_path']}/ip_plan.json") as file:
        dict_ip_plan = json.load(file)
    logger.info(f"IP plan file {path['output_path']}/ip_plan.json read")

except FileNotFoundError:
    logger.error(f"IP plan file {path['output_path']}/ip_plan.json not found. Run <0.preparation.py> Program exit")
    quit()

except IndexError:
    logger.error(f"IP plan file {path['output_path']}/ip_plan.json is written with the wrong title length. Program exit")
    quit()

# Get Zones
logger.info(f"Get zones")
dict_zones = {}
for line in dict_ip_plan:
    if (line["zone"] and 
        line["0_ip_ug"] and 
        line["1_ip_ug"] and 
        line["2_ip_ug"] and 
        line["mask"]):
            try:
                dict_zones[f'{MC_PREFIX}{line["zone"]}']["networks"].append(str(ipaddress.IPv4Interface(f"{line['1_ip_ug']}/{line['mask']}").network))
            except:
                dict_zones[f'{MC_PREFIX}{line["zone"]}'] = { "networks": [] }
                dict_zones[f'{MC_PREFIX}{line["zone"]}']["networks"].append(str(ipaddress.IPv4Interface(f"{line['1_ip_ug']}/{line['mask']}").network))
    elif line["zone"]:
        try: 
            dict_zones[f'{MC_PREFIX}{line["zone"]}']["networks"]
        except KeyError:
            dict_zones[f'{MC_PREFIX}{line["zone"]}'] = { "networks": [] }

logger.info(f"Connecting to UG MC, template: {UG_MC_template_UTM_selected['name']}")

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


logger.info(f"Deploy zones")

deployed_zones = []
for zone in dict_zones:
    try:
        request_zone = {
            "name": f"{zone}",
            "dos_profiles": [                   # DOS Protection
                {
                    "enabled": False,
                    "kind": "syn",
                    "alert_threshold": 300,  # 0-200000
                    "drop_threshold": 600    # 0-200000
                },
                {
                    "enabled": False,
                    "kind": "udp",
                    "alert_threshold": 300,  # 0-200000
                    "drop_threshold": 600    # 0-200000
                },
                {
                    "enabled": False,
                    "kind": "icmp",
                    "alert_threshold": 300,  # 0-200000
                    "drop_threshold": 600    # 0-200000
                }
            ], 
            "services_access": [
                {
                    "enabled": True,
                    "allowed_ips": [""],
                    "service_id": "ffffff03-ffff-ffff-ffff-ffffff000001"    # Ping
                },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000002"    # SNMP
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000004"    # Captive portal and block pages
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000005"    # Control XML-RPC
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000006"    # Cluster
                # },
                {
                    "enabled": True,
                    "allowed_ips": [""],
                    "service_id": "ffffff03-ffff-ffff-ffff-ffffff000007"    # VRRP
                },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000008"    # Administrative console
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000009"    # DNS
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000010"    # HTTP/HTTPS proxy
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000011"    # Authorization agent
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000012"    # SMTP(S) proxy
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000013"    # POP3(S) proxy
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000014"    # CLI over SSH
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000015"    # VPN
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000017"    # SCADA
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000018"    # Reverse proxy
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000019"    # Web portal
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000022"    # SAML server
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000023"    # Log analizer
                # },
                {
                    "enabled": True,
                    "allowed_ips": [""],
                    "service_id": "ffffff03-ffff-ffff-ffff-ffffff000024"    # OSPF
                },
                {
                    "enabled": True,
                    "allowed_ips": [""],
                    "service_id": "ffffff03-ffff-ffff-ffff-ffffff000025"    # BGP
                },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000030"    # RIP
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000026"    # SNMP proxy
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000027"    # SSH proxy
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000028"    # Multicast
                # },
                # {
                #     "enabled": True,
                #     "allowed_ips": [""],
                #     "service_id": "ffffff03-ffff-ffff-ffff-ffffff000029"    # NTP service
                # }
            ]
        }

        # antispoofing DISABLED
        # if dict_zones[zone]["networks"]:
        #     request_zone["enable_antispoof"] = True
        #     request_zone["networks"] = dict_zones[zone]["networks"]
        # else:
        #     request_zone["enable_antispoof"] = False
        #     request_zone["networks"] = []
        request_zone["enable_antispoof"] = False
        request_zone["networks"] = []

        response_deploy_zone = UG_MC_server.v1.ccnetmanager.zone.add(UG_MC_auth_token, UG_MC_template_UTM_selected["id"], request_zone)
        request_zone = ""
        if len(response_deploy_zone) == 36:
            logger.success(f"Zone <{zone}> deployed successfully")
            deployed_zones.append(response_deploy_zone)
        else:
            logger.error(f"Trouble with delpoying zone <{zone}>, error: {error.faultString}")

    except xmlrpc.client.Fault as error:
        logger.error(f"Trouble with delpoying zone <{zone}>, error: {error.faultString}")

# Create rule with zones
if deployed_zones:
    try:
        response_deploy_rule = UG_MC_server.v1.ccfirewall.rule.add(UG_MC_auth_token, UG_MC_template_UTM_selected["id"], {
            "position": "1",
            "position_layer": "pre",
            "action": "drop",
            "enabled": False,
            "name": f"Creating zones at {name_time}",
            "src_zones": deployed_zones,
            "dst_zones": deployed_zones,
            })
        logger.success(f"Rule <Creating zones at {name_time}> deployed successfully")
    except xmlrpc.client.Fault as error:
        logger.error(f"Trouble with delpoying rule <Creating zones at {name_time}>, error: {error.faultString}")
else:
    logger.error(f"Zones not found")

# Release token
release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
if not release_token:
    logger.success("Token released")
else:
    logger.error("Token not released")
