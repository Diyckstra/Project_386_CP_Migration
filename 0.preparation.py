from functions import *
from variables import *

# ------------ B E G I N ------------

# Logs
name_time = datetime.now().strftime("%d.%m.%Y")
logger.add(f"{log_0}_{name_time}.log", backtrace=True, diagnose=True, rotation="250 MB")
logger.info(f"Script starts")

# Create paths
for i in path:
    isExist = os.path.exists(path[i])
    if not isExist:
        os.makedirs(path[i])
logger.info(f"Directories created")

# Open CSV file
dict_ip_plan = []
try:
    with open(f"{path['input_path']}/{ip_plan_selected}", mode ='r', encoding = 'utf-8-sig', newline = '') as csvfile:
        csvFile = csv.reader(csvfile, delimiter=';', dialect='excel')

        for count, column in enumerate(csvFile):
            if count > 0 :
                tmp = {
                    'physical': column[0],
                    'logical':  column[1],
                    'cp_iface': column[2],
                    '0_ip_cp':  column[5],
                    '1_ip_cp':  column[3],
                    '2_ip_cp':  column[4],
                    'zone':     column[6],
                    '0_ip_ug':  column[9],
                    '1_ip_ug':  column[7],
                    '2_ip_ug':  column[8],
                    'mask':     column[10]
                }
                if tmp["0_ip_ug"] and tmp["1_ip_ug"] and tmp["2_ip_ug"] and tmp["mask"]:
                    tmp["0_ip_ug"], tmp["mask"] = check_ip(count, tmp["0_ip_ug"], tmp["mask"])
                    tmp["1_ip_ug"], tmp["mask"] = check_ip(count, tmp["1_ip_ug"], tmp["mask"])
                    tmp["2_ip_ug"], tmp["mask"] = check_ip(count, tmp["2_ip_ug"], tmp["mask"])

                if tmp["zone"]:
                    if (len(tmp["zone"]) > 50 or 
                        tmp["zone"].find(".") != -1 or 
                        tmp["zone"].find(",") != -1 or 
                        tmp["zone"].find("#") != -1 or 
                        tmp["zone"].find("№") != -1 or
                        tmp["zone"].find("%") != -1 or
                        tmp["zone"].find("&") != -1 or
                        tmp["zone"].find("?") != -1):
                        logger.error(f"Zone <{tmp['zone']}> a is entered incorrectly in the line number {count}, enter the correct zone in the file")

                dict_ip_plan.append(tmp)
                tmp = ""
    logger.info(f"CSV IP plan file {path['input_path']}/{ip_plan_selected} read")

except FileNotFoundError:
    logger.error(f"CSV IP plan file {path['input_path']}/{ip_plan_selected} not found. Program exit")
    quit()

except IndexError:
    logger.error(f"CSV IP plan file {path['input_path']}/{ip_plan_selected} is written with the wrong title length. Program exit")
    quit()

if dict_ip_plan:
    with open(f'{path["output_path"]}/ip_plan.json', 'w', encoding='utf-8') as f:
        json.dump(dict_ip_plan, f, ensure_ascii=False, indent=4)
    logger.success(f"IP plan are recorded to <{path['output_path']}/ip_plan.json>")
else:
    logger.error(f"No IP plan created")
