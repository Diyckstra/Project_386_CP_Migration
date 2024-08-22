import os
import json
import sys
import csv
import ipaddress
import ssl
import http.client
import xmlrpc.client
from loguru import logger
from datetime import datetime
from pprint import pprint

# # For API configs

# # Main CP API function
# def CP_api_call(server, port, command, json_payload, sid):
#     # https://ip_addr:port/web_api/command
#     url = '/web_api/' + command
#     if sid == '':
#         headers = {'Content-Type' : 'application/json'}
#     else:
#         headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}

#     context = ssl._create_unverified_context()
#     httpClient = http.client.HTTPSConnection(server, port, timeout=60, context=context)

#     try:
#         httpClient.request("POST", url, json.dumps(json_payload), headers)
#         response    = httpClient.getresponse()
#         status      = response.status
#         reason      = response.reason
#         reply       = response.read()
#         httpClient.close()
#     except ConnectionRefusedError:
#         return 504, {"message": "API server is not available"}
#     except Exception as error:
#         print("An exception occurred:", error)

#     if status == 200:
#         return status, json.loads(reply)
#     else:
#         return status, {"message": reason}

# # get hosts, networks, wildcards from SMS
# def CP_get_objects(server, port, sid, object_type, membership):
#     if membership:
#         body = { "limit": LIMIT, "offset": 0, "details-level": "full", "show-membership": "true" }
#     else:
#         body = { "limit": LIMIT, "offset": 0, "details-level": "full" }
#     status, response = CP_api_call(server, port, object_type, body, sid)
#     if status == 200:
#         if response["total"] > 0: 
#             objects = response["objects"]
#             offset = LIMIT
#             while response["total"] > response["to"]:
#                 if membership:
#                     body = { "limit": LIMIT, "offset": offset, "details-level": "full", "show-membership": "true" }
#                 else:
#                     body = { "limit": LIMIT, "offset": offset, "details-level": "full" }
#                 status, response = CP_api_call(server, port, object_type, body, sid)
#                 objects += response["objects"]
#                 offset += LIMIT
#             return status, { "total": response["total"], "items": objects }
#         else:
#             return status, { "total": 0, "items": [] }
#     else:
#         return status, response

# def CP_SMS_get_policies(server, port, sid):
#     body = { }
#     status, response = CP_api_call(server, port, 'show-access-layers', body, sid)
#     policy = []
#     for i in response['access-layers']:
#         policy.append(i["name"])
#     return policy

# def CP_SMS_transform_rule(field_in_section, cashe_uid ):
#     field_in_section.pop("uid")
#     field_in_section.pop("domain")
#     field_in_section.pop("meta-info")
#     transform_objects = [
#         "source",
#         "destination",
#         "service",
#         "vpn",
#         "content",
#         "time",
#         "action",
#         "install-on",
#         "track"
#     ]
#     for oo in transform_objects:
#         if oo != "action" and oo != "track":
#             oos = []
#             for oo_ in field_in_section[oo]:
#                 try:
#                     oos.append(cashe_uid[oo_])
#                 except:
#                     print(f"No name: {oo_}")
#             if oos:
#                 field_in_section[oo] = oos
#         elif oo == "action" :
#             field_in_section[oo] = cashe_uid[field_in_section[oo]]
#         elif oo == "track" :
#             field_in_section[oo]["type"] = cashe_uid[field_in_section[oo]["type"]]
#     return field_in_section

# def CP_SMS_get_rulebase_from_policy(server, port, sid, name):
#     body = { "name": name, "limit": LIMIT, "offset": 0, "details-level": "full", "use-object-dictionary": "true" }
#     status, response = CP_api_call(server, port, 'show-access-rulebase', body, sid)
#     if response["total"] > 0: 
#         objects = response["rulebase"]
#         cashe_uid = {}
#         for a in response["objects-dictionary"]:
#             cashe_uid[a["uid"]] = a["name"]
#         offset = LIMIT
#         while response["total"] > response["to"]:
#             body = { "name": name, "limit": LIMIT, "offset": offset }
#             status, response = CP_api_call(server, port, 'show-access-rulebase', body, sid)
#             objects += response["rulebase"]
#             offset += LIMIT
#             for a in response["objects-dictionary"]:
#                 cashe_uid[a["uid"]] = a["name"]
#         for field_in_package in objects:
#             if field_in_package["type"] == "access-section":
#                 field_in_package.pop("uid")
#                 for field_in_section in field_in_package["rulebase"]:
#                     field_in_section = CP_SMS_transform_rule(field_in_section, cashe_uid)
#             else:
#                 field_in_package = CP_SMS_transform_rule(field_in_package, cashe_uid)

#         return { "total": response["total"], "rulebase": objects }
#     else: 
#         return { "total": response["total"], "rulebase": [] }

# # For text configs
# def CP_NGFW_parse_config(path, config_name, config):
#     parsed_config = {
#         "snmp": [],
#         "arp": [],
#         "interface": [],
#         "static_route": [],
#         "pbr": [],
#         "other": []
#         }

#     for line_config in config:
#         if line_config:
            
#             # Comment && empty lines
#             if line_config[0] == '#' or line_config[0] == ' ':
#                 None

#             # SNMP
#             elif line_config.find("set snmp ") != -1:
#                 parsed_config["snmp"].append(line_config)

#             # ARP
#             elif line_config.find("add arp proxy ") != -1:
#                 parsed_config["arp"].append(line_config)

#             # PBR
#             elif line_config.find("set pbr ") != -1:
#                 parsed_config["pbr"].append(line_config)

#             # Static Route
#             elif line_config.find("set static-route ") != -1:
#                 parsed_config["static_route"].append(line_config)

#             # Interface
#             elif ((line_config.find("add interface ") != -1) or 
#                 (line_config.find("set interface ") != -1) or 
#                 (line_config.find("set pim interface ") != -1) or 
#                 (line_config.find("set bonding group ") != -1) or
#                 (line_config.find("add bonding group ") != -1) or
#                 (line_config.find("set igmp interface ") != -1)):
#                 parsed_config["interface"].append(line_config)

#             # Other
#             else:
#                 parsed_config["other"].append(line_config)

#     return parsed_config

# USERGATE

# # get token
# def UG_get_token(SERVER, PORT, USER, PASSWORD):
#     # creating a request link
#     #server = xmlrpc.client.ServerProxy('http://' + SERVER + ':4040/rpc', verbose=False)
#     server = xmlrpc.client.ServerProxy(f'http://{SERVER}:{PORT}/rpc', verbose=False)

#     # get token
#     try:
#         res = server.v2.core.login(USER, PASSWORD, {})
#         auth_token = res['auth_token']
#     except ValueError:
#             print("Trouble with getting token in getting network object")
#             quit()

#     return server, auth_token

# other
def check_ip(number, ip, mask):
    try:
        ipaddress.IPv4Interface(f"{ip}/{mask}")
        return ip, mask
    except ipaddress.AddressValueError:
        new_ip = input(f"IP address <{ip}> a is entered incorrectly in the line number {number}, enter the correct address: ")
        return check_ip(number, new_ip, mask)
    except ipaddress.NetmaskValueError:
        new_mask = input(f"IP mask <{mask}> a is entered incorrectly in the line number {number}, enter the correct mask: ")
        return check_ip(number, ip, new_mask)














