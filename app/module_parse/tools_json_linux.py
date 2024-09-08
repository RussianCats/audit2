from app.module_parse import *


def parseJSONLinux(_pathJSONLinux):
    report = __getInfoReport(_pathJSONLinux, deepcopy(infoReport))
    return report
    



def __getInfoReport(_path, _report):
    try:
        # Opening JSON file
        f = open(_path)
        
        # returns JSON object as 
        # a dictionary
        result = json.load(f)

        # Iterating through the json
        # list
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
            _report["ram"] = result["ram"]
            _report["disk"] = result["disk"]

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

        # Closing file
        f.close()
        logger.info(f"Собран:   {_path} \t\t {_report["hostname"]}")

        return _report

    except Exception as e:
        logger.error( "json: " + str(_path) + "! невозможно прочитать отчет: " + str(e))
        return None
    