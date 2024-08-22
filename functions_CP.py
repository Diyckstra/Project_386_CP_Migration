from functions import *
from variables import LIMIT

# Main CP API function
def CP_api_call(server, port, command, json_payload, sid):
    # https://ip_addr:port/web_api/command
    url = '/web_api/' + command
    if sid == '':
        headers = {'Content-Type' : 'application/json'}
    else:
        headers = {'Content-Type' : 'application/json', 'X-chkp-sid' : sid}

    context = ssl._create_unverified_context()
    httpClient = http.client.HTTPSConnection(server, port, timeout=60, context=context)

    try:
        httpClient.request("POST", url, json.dumps(json_payload), headers)
        response    = httpClient.getresponse()
        status      = response.status
        reason      = response.reason
        reply       = response.read()
        httpClient.close()
    except ConnectionRefusedError:
        return 504, {"message": "API server is not available"}
    except Exception as error:
        print("An exception occurred:", error)

    if status == 200:
        return status, json.loads(reply)
    else:
        return status, {"message": reason}

# Get hosts, networks, wildcards and etc from SMS
def CP_get_objects(server, port, sid, object_type, membership):
    if membership:
        body = { "limit": LIMIT, "offset": 0, "details-level": "full", "show-membership": "true" }
    else:
        body = { "limit": LIMIT, "offset": 0, "details-level": "full" }
    status, response = CP_api_call(server, port, object_type, body, sid)
    if status == 200:
        if response["total"] > 0: 
            objects = response["objects"]
            offset = LIMIT
            while response["total"] > response["to"]:
                if membership:
                    body = { "limit": LIMIT, "offset": offset, "details-level": "full", "show-membership": "true" }
                else:
                    body = { "limit": LIMIT, "offset": offset, "details-level": "full" }
                status, response = CP_api_call(server, port, object_type, body, sid)
                objects += response["objects"]
                offset += LIMIT
            return status, { "total": response["total"], "items": objects }
        else:
            return status, { "total": 0, "items": [] }
    else:
        return status, response

def CP_SMS_transform_rule(field_in_section, cashe_uid ):
    field_in_section.pop("uid")
    field_in_section.pop("domain")
    field_in_section.pop("meta-info")
    transform_objects = [
        "source",
        "destination",
        "service",
        "vpn",
        "content",
        "time",
        "action",
        "install-on",
        "track"
    ]
    for oo in transform_objects:
        if oo != "action" and oo != "track":
            oos = []
            for oo_ in field_in_section[oo]:
                try:
                    oos.append(cashe_uid[oo_])
                except:
                    print(f"No name: {oo_}")
            if oos:
                field_in_section[oo] = oos
        elif oo == "action" :
            field_in_section[oo] = cashe_uid[field_in_section[oo]]
        elif oo == "track" :
            field_in_section[oo]["type"] = cashe_uid[field_in_section[oo]["type"]]
    return field_in_section

def CP_SMS_get_rulebase_from_policy(server, port, sid, name):
    body = { "name": name, "limit": LIMIT, "offset": 0, "details-level": "full", "use-object-dictionary": "true" }
    status, response = CP_api_call(server, port, 'show-access-rulebase', body, sid)
    if status == 200 and response["total"] > 0: 
        objects = response["rulebase"]
        cashe_uid = {}
        for a in response["objects-dictionary"]:
            cashe_uid[a["uid"]] = a["name"]
        offset = LIMIT
        while response["total"] > response["to"]:
            body = { "name": name, "limit": LIMIT, "offset": offset }
            status, response = CP_api_call(server, port, 'show-access-rulebase', body, sid)
            objects += response["rulebase"]
            offset += LIMIT
            for a in response["objects-dictionary"]:
                cashe_uid[a["uid"]] = a["name"]

        rules = []
        for field_in_package in objects:
            section = "default-global-section"
            if field_in_package["type"] == "access-section":
                field_in_package.pop("uid")
                for field_in_section in field_in_package["rulebase"]:
                    field_in_section = CP_SMS_transform_rule(field_in_section, cashe_uid)
                    field_in_section["section"] = field_in_package["name"]
                    try:
                        field_in_section["name"]
                    except KeyError:
                        field_in_section["name"] = ""
                    field_in_section.pop("type")
                    rules.append(field_in_section)
            else:
                field_in_package = CP_SMS_transform_rule(field_in_package, cashe_uid)
                field_in_package["section"] = section
                try:
                    field_in_package["name"]
                except KeyError:
                    field_in_package["name"] = ""
                field_in_package.pop("type")
                rules.append(field_in_package)

        rules[-1]["name"] = "Cleanup Rule"

        return { "total": response["total"], "rulebase": rules }
    else: 
        return { "total": response["total"], "rulebase": [] }