from app.module_parse import *
from copy import deepcopy
import json

def parseJSONLinux(_pathJSONLinux):
    report = __getInfoReport(_pathJSONLinux, deepcopy(infoReport))
    return report
    


# Рекурсивная функция для замены null на ""
def replace_nulls(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if value is None:  # Проверяем, если значение null (None в Python)
                data[key] = ""
            else:
                replace_nulls(value)  # Рекурсивно обрабатываем вложенные словари
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if item is None:
                data[i] = ""
            else:
                replace_nulls(item)  # Рекурсивно обрабатываем вложенные списки



def __getInfoReport(_path, _report):
    try:
        # Opening JSON file
        f = open(_path)
        
        # returns JSON object as 
        # a dictionary
        result = json.load(f)

        replace_nulls(result)

        # Iterating through the json
        # list
        try:
            if result["form"] == "bash_script":
                _report["hostname"] = result["hostname"]
                _report["uuid"] = result["uuid"]
                _report["ip"] = result["ip"] # в массиве
                _report["mac"] = result["mac"] # в массиве
                _report["cpu"] = result["cpu"]
                _report["videoadapter"] = '; '.join(result["videoadapter"])  # в массиве
                _report["cd_dvd"] = result["cd_dvd"]
                _report["motherboard"]["vendor"] = result["motherboard"]["vendor"]
                _report["motherboard"]["model"] = result["motherboard"]["model"]
                _report["os"]["small"] = result["os"]["small"]
                _report["os"]["full"] = result["os"]["full"]
                _report["ram"] = result["ram"].replace(" GB", " ГБ")
                _report["disk"] = result["disk"].replace(" GB", " ГБ")

                try:
                    for ipt in result["ipt_list"]: # в массиве
                        _report["ipt_list"].append([ipt["name"], ipt["version"], ipt["installDate"]])
                except:
                    _report["ipt_list"] = []
                # _report["app_list"] = result["app_list"] # в массиве
                _report["monitor"] = result["monitor"]  # в массиве
                _report["keyboard"] = result["keyboard"] 
                _report["mouse"] = result["mouse"] 
                _report["org"]["inventory"] = result["org"]["inventory"]
                _report["org"]["cabinet"] = result["org"]["cabinet"]
                _report["org"]["structural"] = result["org"]["structural"]  # в массиве
                _report["org"]["FIO"] = result["org"]["FIO"]  # в массиве
                _report["org"]["address"] = result["org"]["address"]

        except:
            _report["hostname"] = result["hostname"]        
            _report["uuid"] = result["uuid"]               
            _report["ip"] = result["ip"] # в массиве        
            _report["mac"] = result["mac"] # в массиве      
            _report["cpu"] = '; '.join(result["tech"]["cpu"])                   
            _report["videoadapter"] = '; '.join(result["tech"]["videoadapter"])
            _report["cd_dvd"] = result["tech"]["cd_dvd"]
            _report["motherboard"]["vendor"] = result["tech"]["motherboard"]["vendor"]
            _report["motherboard"]["model"] = result["tech"]["motherboard"]["model"]
            _report["os"]["small"] = result["tech"]["os"]["small"]
            _report["os"]["full"] = result["tech"]["os"]["full"]
            _report["ram"] = result["tech"]["ram"]

            # только общий объем не USB устройств
            tmp_collect = 0
            for tmp_disk in result["tech"]["disk"] : # в массиве
                if not(tmp_disk[0] in "USB Device"):
                    tmp_collect += float(tmp_disk[1].replace(" ГБ", "").replace(",", "."))
            _report["disk"] = f"{int(tmp_collect)} ГБ" 

            try:
                for ipt in result["app"]: # в массиве
                    _report["app_list"].append([ipt[0], ipt[1], ipt[2]])
            except:
                _report["app_list"] = []

            _report["monitor"] = result["per"]["monitor"]  # в массиве
            _report["keyboard"] = result["per"]["keyboard"] 
            _report["mouse"] = result["per"]["mouse"] 
            _report["type_arm"] = result["org"]["type_arm"]
            _report["description"] = result["org"]["description"]
            _report["org"]["inventory"] = result["org"]["inventory"]
            _report["org"]["cabinet"] = result["org"]["cabinet"][0] 
            _report["org"]["address"] = result["org"]["cabinet"][1]
            
            for tmp_emp in result["org"]["empl"]: 
                _report["org"]["FIO"].append(tmp_emp[0])  # в массиве
                _report["org"]["position"].append(tmp_emp[1])  # в массиве
                _report["org"]["structural"].append(tmp_emp[2])  # в массиве

        _report["cpu"] = _report["cpu"].split('CPU @')[0]
        _report["cpu"] = _report["cpu"].split('@')[0]
        # print(_report)

        # Closing file
        f.close()
        logger.info(f"Собран:   {_path} \t\t {_report["hostname"]}")

        return _report

    except Exception as e:
        logger.error( "json: " + str(_path) + "! невозможно прочитать отчет: " + str(e))
        return None
    