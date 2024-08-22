from functions import *
from functions_UG import UG_get_token, UG_release_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_6}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
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

# ------------ P O L I C Y ------------------------------------------------
logger.info(f"Deploy Policy <{name_policy_selected}>")

# Open policy file
try:
    with open(f"{path['sms_config_path']}/{name_policy_selected}") as file:
        POLICY = json.load(file)
    logger.info(f"File {path['sms_config_path']}/{name_policy_selected} opened")
# File not found
except FileNotFoundError:
    logger.error(f"File {path['sms_config_path']}/{name_policy_selected} not found")
    quit()

# Open Service dictionary file
try:
    with open(f"{path['output_path']}/Services_UID.json") as file:
        dict_service_uid = json.load(file)
    logger.info(f"File {path['output_path']}/Services_UID.json opened")
# File not found
except FileNotFoundError:
    logger.error(f"File {path['output_path']}/Services_UID.json not found")
    quit()

# Get network dictionery
try:
    dictionary_network = UG_MC_server.v1.ccnlists.lists.list(UG_MC_auth_token, UG_MC_template_objects['id'], "network", 0, 2000, {}, {})
    if dictionary_network["count"] > 0:
        logger.success(f"Object dictionary received, number of elements: {dictionary_network['count']}")
    else:
        logger.error(f"Object dictionary not received, number of elements:  {dictionary_network['count']}")

        # Release token
        release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
        quit()

except Exception:
    logger.error(f"Object dictionary not received.")
    # Release token
    release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
    quit()

# Deploy rules
for rule in POLICY["rulebase"]:

    # Avoid rule Cleanup
    if rule["name"] == "Cleanup Rule":
        continue

    # Fix Name
    if rule["name"]:
        rule_name = f'Rule {rule["rule-number"]} - {rule["name"]}'
    else:
        rule_name = f'Rule {rule["rule-number"]}'

    # Fix Source 
    id_source_ips = []
    if rule["source"] != ['Any']:
        not_find_source = rule["source"].copy()
        for source_ip in rule["source"]:
            for address in dictionary_network['items']:
                if source_ip == address["name"]:
                    id_source_ips.append(['list_id', address["id"]])
                    not_find_source.pop(not_find_source.index(address["name"]))
                    break

        if not_find_source:
            logger.warning(f"{rule_name}: not finding elemets in source: {not_find_source}")

    # Fix Destination
    id_destination_ips = []
    if rule["destination"] != ['Any']:
        not_find_destination = rule["destination"].copy()
        for dest_ip in rule["destination"]:
            for address in dictionary_network['items']:
                if dest_ip == address["name"]:
                    id_destination_ips.append(['list_id', address["id"]])
                    not_find_destination.pop(not_find_destination.index(address["name"]))
                    break

        if not_find_destination:
            logger.warning(f"{rule_name}: not finding elemets in destination: {not_find_destination}")

    # Fix Service
    id_services = []
    if rule['service'] != ['Any']:
        for service in rule['service']:
            try:
                id_services.append(dict_service_uid[service])
            except:
                logger.warning(f"Service <{service}> not added to rule <{rule_name}>")

    # Deploy Rule
    try:
        logger.debug(f"Deploy rule <{rule_name}>")
        response_deploy_rule = UG_MC_server.v1.ccfirewall.rule.add(
            UG_MC_auth_token,
            UG_MC_template_UTM_selected['id'],
            {
                "position": rule["rule-number"],                # object position in whole list, integer value starting with 1, to add new item to the bottom use string value "last"
                "position_layer": "post",                       # rule position layer, possible values are: "pre", "post"
                "action": rule["action"].lower(),               # accept", "drop"
                "enabled": rule["enabled"],                     # Boolean
                "name": rule_name,                              # String
                "description": rule["comments"],                # String
                "src_ips": id_source_ips,                       # List<TaggedValue>
                "src_ips_negate": rule["source-negate"],        # Boolean
                "dst_ips": id_destination_ips,                  # List<TaggedValue>
                "dst_ips_negate": rule["destination-negate"],   # Boolean
                "services": id_services,                        # List<TaggedValue>
                "services_negate": rule["service-negate"],      # Boolean
                "log": True,                                    # Boolean enable logging
                'log_session_start': True,                      # Boolean enable logging at first packet in session
                "limit": False,                                 # Boolean enable limit logging

                # "limit_value": "3/h",                           # String "1/s", "1/m", "1/h", "1/d", default = "3/h"
                # "limit_burst": 5,                               # Integer guaranteed number of events to be logged
                # "src_zones":                                    # List<UID>
                # "src_zones_negate":                             # Boolean
                # "dst_zones":                                    # List<UID>
                # "dst_zones_negate":                             # Boolean
            }
        )

        if len(response_deploy_rule) == 36:
            logger.success(f"Rule <{rule_name}> deployed")
        else:
            logger.error(f"Rule <{rule_name}> not deployed")
    except Exception as error:
        logger.error(f"Rule <{rule_name}> not deployed, error: {error}")


# Release token
release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
if not release_token:
    logger.success("Token released")
else:
    logger.error("Token not released")


# Display rules
# response_deploy_rule = UG_MC_server.v1.ccfirewall.rules.list(
#     UG_MC_auth_token,
#     UG_MC_template_UTM_selected['id'],
#     0,
#     500,
#     {},
#     "template"
# )
# pprint(response_deploy_rule)

#    {'action': 'accept',
#     'active': True,
#     'apps': [],
#     'apps_negate': False,
#     'cc_network_devices': [],
#     'cc_network_devices_negate': False,
#     'description': '',
#     'dst_ips': [['list_id', '27a3d7c2-93fd-4209-a754-1416e26aea50']],
#     'dst_ips_negate': False,
#     'dst_zones': [],
#     'dst_zones_negate': False,
#     'enabled': True,
#     'fragmented': 'ignore',
#     'grid_position': 160,
#     'id': '4f7accb8-5a7b-4d27-919c-29c960e51844',
#     'limit': False,
#     'limit_burst': 5,
#     'limit_value': '3/h',
#     'log': True,
#     'log_session_start': True,
#     'name': '',
#     'position': 9,
#     'position_layer': 'post',
#     'scenario_rule_id': False,
#     'send_host_icmp': '',
#     'services': ['18c29d02-e235-a256-1015-a3342f02f55c',
#                  '99a71ba2-910e-fb34-fe6f-46544c8898d8',
#                  '8bbc211e-e6cb-d6c4-3ef2-3ad6dbc3586e',
#                  'a1d23188-0552-ee8e-fde2-95fe616a5ef5',
#                  'd844bfba-d503-651f-39f1-1781f1b92fdb',
#                  '05b18f67-ba13-a382-945d-8cc3f2ee72ce',
#                  'aefd9446-d41b-521e-95ef-640793174e34'],
#     'services_negate': False,
#     'src_ips': [['list_id', '1772b4b5-3398-dc0f-7db2-f75c52ec056f'],
#                 ['list_id', '601112ff-758f-0314-c96b-2e5c13a91675'],
#                 ['list_id', '1eb50b6c-31e2-7c86-4bc7-123b8272637a'],
#                 ['list_id', '77359aa4-550f-73c1-051f-afa947b31998']],
#     'src_ips_negate': False,
#     'src_zones': [],
#     'src_zones_negate': False,
#     'template_id': '848744f4-c338-4a81-aab6-2cfb105d170f',
#     'time_restrictions': [],
#     'users': []},