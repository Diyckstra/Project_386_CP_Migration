
LIMIT = 50
MC_PREFIX = "MC_"

# Path
path = {
    "log_path": "logs",
    "input_path": "input",
    "output_path": "output",
    "sms_config_path": "CP_SMS_config"
}

# Credentionals files
CP_SMS_creds_file   = "checkpoint_sms.json"
UG_MC_creds_file    = "usergate_mc.json"
UG_UTM_1_creds_file = "usergate_utm_cluster_1.json"     # ---
UG_UTM_2_creds_file = "usergate_utm_cluster_2.json "    # ----
UG_UTM_selected_creds_file = UG_UTM_1_creds_file        # Change to selected cluster!!!

# Templates
UG_MC_template_objects_default =    {
        "name": "UserGate Libraries template",
        "id": "b643aade-00c1-4d96-b854-7c9f50dce4f9"
    }
UG_MC_template_objects =            {
        "name": "General Library",
        "id": "20bb74b3-09a3-422c-97fb-dd21d1154a96"
    }
UG_MC_template_UTM_1 =              {                       # ----
        "name": "Inside",
        "id": "d86463c4-52a9-4882-9027-cac807875096"
    }
UG_MC_template_UTM_2 =              {                       # ----
        "name": "Outside",
        "id": "9faa2d19-1bba-4a68-a2f0-50862c5969a9"
    }

UG_MC_template_UTM_selected = UG_MC_template_UTM_1      # Change to selected cluster!!!

# Name file of csv IPs
ip_plan_1 = "inside.csv"                                # ---
ip_plan_2 = "outside.csv"                               # ----
ip_plan_selected = ip_plan_1                            # Change to selected cluster!!!

# Name Policys
name_policy_1 = "Policy_Network.json"
name_policy_2 = "Policy_policy_WAN-FW-4800 Security.json"
name_policy_selected = name_policy_1

# Log files
log_0 = f"{path['log_path']}/Preparation"                       # 0.preparation.py
log_1 = f"{path['log_path']}/UG_MC_show_templates"              # 1.UG_MC_show_templates.py
log_2 = f"{path['log_path']}/UG_MC_deploy_zones_from_csv"       # 2.UG_MC_deploy_zones_from_csv.py
log_3 = f"{path['log_path']}/CP_SMS_get_config"                 # 3.CP_SMS_get_config.py
log_4 = f"{path['log_path']}/UG_MC_deploy_objects_from_CP_SMS"  # 4.UG_MC_deploy_objects_from_CP_SMS.py
log_5 = f"{path['log_path']}/UG_MC_deploy_services_from_CP_SMS" # 5.UG_MC_deploy_services_from_CP_SMS.py
log_6 = f"{path['log_path']}/UG_MC_deploy_policy_from_CP_SMS"   # 6.UG_MC_deploy_policy_from_CP_SMS.py
log_7 = f"{path['log_path']}/UG_UTM_deploy_ifaces_from_csv"     # 7.UG_UTM_deploy_ifaces_from_csv.py
log_8 = f"{path['log_path']}/UG_UTM_deploy_route_from_cfg"      # 8.UG_UTM_deploy_route_from_cfg.py
log_9 = f"{path['log_path']}/UG_UTM_deploy_arp_from_cfg"        # 9.UG_UTM_deploy_arp_from_cfg.py
log_10 = f"{path['log_path']}/UG_UTM_deploy_pbr_from_cfg"       # 10.UG_UTM_deploy_pbr_from_cfg.py
# https://static.usergate.com/manuals/api/utm-6.1.x/methods/netmanager.html#v1netmanagervirtualrouteradd
# https://static.usergate.com/manuals/api/mc-7