from app.module_parse import *
from app.module_files.work_files import readFileToList



def parseXML(_pathXML):

    # print(readExcelFile('/home/penguin/tmp/tauditV2/database/ЦФО Госветслужбы. Таблица для заполнения.xlsx', 9))
    report = __getInfoReport(_pathXML, 
                             deepcopy(infoReport), 
                             readFileToList(f"{config.CONFIG.LIBPATH}/module_files/SZI.txt"),
                             readFileToList(f"{config.CONFIG.LIBPATH}/module_files/APP.txt")
    )
    return report




def __getInfoReport( _path, _report, _arrIPTs, _arrAPPs):
    
    # получание данных с xml 
    try:
        tree = ET.parse(_path)
        root = tree.getroot()

        # поиск начинки системы 
        Title = root.findall('.//Group[Title="Сеть"]/Item/Value')
        # дописать сбор по всем ip
        _report["ip"].append(Title[0].text) 
        _report["mac"].append(Title[1].text) 
        
        if(CONFIG.DISKINFO):
            _report["disk"] = list()
            Item = root.findall('.//Group[Title="Хранение данных"]/Item')
            for Item in root.findall('.//Group[Title="Хранение данных"]/Item'):
                value = Item.findall('.//*')
                if(value[2].text == "529"):
                    _report["cd_dvd"] = value[3].text
                if(value[2].text == "528"):
                    _report["disk"].append(value[3].text)
            
            disksList = ""
            for disk in _report["disk"]:
                if(not(disk.find("USB") + 1)):
                    disksList = disksList + "; " +  disk.replace(' ATA Device', '').replace(' SCSI Disk Device', '')
            disksList = disksList[2:]
            _report["disk"] = disksList
        else:
            disksList = root.findall('.//Page[Title="Суммарная информация"]/Group[Title="Разделы"]/Item/Value')
            if disksList:  # Проверка, что список не пуст
                _report["disk"] = disksList[-1].text
                if("ГБ" in _report["disk"]):
                    _report["disk"] = re.match(rf"[\d\.]+\s*ГБ",  _report["disk"]).group()
                elif("МБ" in _report["disk"]):
                    _report["disk"] = str(round(int( _report["disk"].split()[0]) / 1024, 1)) + " ГБ"
                else:
                    pass
        
        try:
            _report["uuid"] = root.find('.//Page[Title="DMI"]/Device[Title="Система"]/Group[Title="Свойства системы"]/Item[Title="Универсальный уникальный ID (GUID)"]/Value').text
        except:
            _report["uuid"] = root.find('.//Page[Title="DMI"]/Device[Title="Система"]/Group[Title="Свойства системы"]/Item[Title="Универсальный уникальный ID"]/Value').text


        #сделать для нескольких процессоров
        _report["cpu"] = root.find('.//Page[Title="CPUID"]/Group[Title="Свойства CPUID"]/Item[Title="Имя ЦП CPUID"]/Value').text
        _report["cpu"] = _report["cpu"].split('CPU @')[0]
        _report["cpu"] = _report["cpu"].split('@')[0]

        Group = root.find('.//Page[Title="Суммарная информация"]')
        try:
            _report["videoadapter"] = Group.find('.//Group[Title="Дисплей"]/Item[ID="523"]/Value').text
        except:
            GroupEx = root.find('.//Page[Title="Устройства Windows"]')
            _report["videoadapter"] = GroupEx.find('.//Group[Title="Видеоадаптеры"]/Item/Title').text
        _report["motherboard"]["vendor"] = Group.find('.//Group[Title="DMI"]/Item[ID="555"]/Value').text
        if(_report["motherboard"]["vendor"] == "None"):
            _report["motherboard"]["vendor"] = ""
        _report["motherboard"]["model"] = Group.find('.//Group[Title="DMI"]/Item[ID="556"]/Value').text
        _report["os"]["small"] = Group.find('.//Group[Title="Компьютер"]/Item[ID="513"]/Value').text
        
        Page = root.find('.//Page[Title="Имя компьютера"]')
        _report["hostname"] = Page.find('.//Device[Title="Имя NetBIOS"]/Item[Title="Имя компьютера"]/Value').text

        Page = root.find('.//Page[Title="Отчёт"]')
        _report["os"]["full"] = Page.find('.//Item[ID="263"]/Value').text
        
        # поиск объема памяти
        _report["ram"] = list()
        for Device in root.findall('.//Device'):
            if((("Устройства памяти" in str(getattr(Device.find('Title'), 'text', None))) and (str(getattr(Device.find('Title'), 'text', None)) != "Устройства памяти / SYSTEM ROM"))):
                for Item in Device.findall(".//Item"):
                    if(getattr(Item.find('Title'), 'text', None) == "Размер"):
                        _report["ram"].append(Item.find("Value").text)
        
        for Device in root.findall('.//Page[Title="Установленные программы"]/Device'):
            # поиск СЗИ 
            for IPT in _arrIPTs:
                if((IPT[0] in str(getattr(Device.find('Title'), 'text', None).replace("\xa0", " "))) and IPT[1]): 
                    IPT[1] = False
                    values = Device.findall('.//Item/Value')
                    _report["ipt_list"].append([str(getattr(Device.find('Title'), 'text', None)), str(values[0].text), str(values[4].text)])
            # поиск приложений
            for APP in _arrAPPs:
                if((APP[0] in str(getattr(Device.find('Title'), 'text', None))) and APP[1]): 
                    APP[1] = False
                    values = Device.findall('.//Item/Value')
                    _report["app_list"].append([str(getattr(Device.find('Title'), 'text', None)), str(values[0].text)])

        # для поиска в автозагрузке
        for Device in root.findall('.//Page[Title="Автозагрузка"]/Device'):
            # поиск докторвеб как агент
            if((getattr(Device.find('Title'), 'text', None) == "SpIDerAgent")):
                _report["ipt_list"].append([str(getattr(Device.find('Title'), 'text', None)), "Автозагрузка", ""])
                
        # почистить данные от изначальных аидовских
        logger.info(f"Собран:   {_path} \t\t {_report["hostname"]}")
        return dataCleaning(_report)
    except Exception as e:
        logger.error( "xml: " + str(_path) + "! невозможно прочитать отчет: " + str(e))
        return None

    


def dataCleaning( _report):
    _report["motherboard"]["vendor"] = _report["motherboard"]["vendor"].replace(".,", ",")

    _report["videoadapter"] = re.sub(r'\s\(.*?\)', '', _report["videoadapter"])

    _report["cd_dvd"] = re.sub(r'\s\(.*?\)', '', _report["cd_dvd"])

    summRam = 0
    for ram in _report["ram"]:
        if(ram.find("ГБ")):
            summRam += int(ram[:-3])
        if(ram.find("МБ")):
            summRam += int(int(ram[:-3]) / 512)
            
    _report["ram"] = str(summRam) + " ГБ"
    return _report


