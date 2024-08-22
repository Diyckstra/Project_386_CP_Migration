from functions import *
from functions_UG import UG_get_token, UG_release_token
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_1}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
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

# Get templates list
response = UG_MC_server.v1.ccdevices.templates.list(UG_MC_auth_token, 0, 1000, {}, [{}])
try:
    response["items"]
    logger.info("Templates received")
except KeyError:
    logger.error("Templates not received")
    release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
    if not release_token:
        logger.success("Token released")
    else:
        logger.error("Token not released")

templates = []
for item in response["items"]:
     #if item["name"] != "UserGate Libraries template":
    templates.append({"name":item["name"], "id":item["id"]})

if templates:
    with open(f'{path["output_path"]}/UG_MC_templates.json', 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=4)
    logger.success(f"Templates are recorded to <{path['output_path']}/UG_MC_templates.json>")
else:
    logger.error(f"No templates created")

# Release token
release_token = UG_release_token(UG_MC_server, UG_MC_auth_token)
if not release_token:
    logger.success("Token released")
else:
    logger.error("Token not released")