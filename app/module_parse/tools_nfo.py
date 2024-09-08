from app.module_parse import *



def parseNFO(_pathNFO):
    report = deepcopy(infoReport)
    report = __getInfoReport(_pathNFO, report)
    return report




def __getInfoReport(_path, _report):
    try:

        # в случае если очтет был забагован и не дописалось закрытие нескольких аттрибутов
        filedata = ""
        # Read in the file
        with open(f'{_path}', 'r+', encoding='utf-16') as file :
            filedata = file.readlines()
            if ("</Data>\n</Category>" in (filedata[len(filedata) - 2] + filedata[len(filedata) - 1])):
                file.write("</Category>\n</Category>\n</MsInfo>")

        tree = ET.parse(_path)
        root = tree.getroot()

        Category = root.find('.//Category[@name="Сведения о системе"]')
        _report["os"]["small"] = Category.find('.//Data[Элемент="Имя ОС"]/Значение').text
        _report["os"]["full"] = _report["os"]["small"] + " " + root.find('.//Data[Элемент="Версия"]/Значение').text

        _report["cpu"] = root.find('.//Data[Элемент="Процессор"]/Значение').text
        _report["cpu"] = _report["cpu"][:_report["cpu"].find(',')].split('CPU @')[0]
        _report["cpu"] = _report["cpu"].split('@')[0]

        _report["motherboard"]["vendor"] = root.find('.//Category[@name="Сведения о системе"]/Data[Элемент="Изготовитель"]/Значение').text
        _report["motherboard"]["model"] = root.find('.//Category[@name="Сведения о системе"]/Data[Элемент="Модель"]/Значение').text
        _report["motherboard"]["vendor"] = _report["motherboard"]["vendor"].replace("System manufacturer", "").replace("To be filled by O.E.M.", "").replace("To Be Filled By O.E.M.", "")
        _report["motherboard"]["model"] = _report["motherboard"]["model"].replace("System Product Name", "").replace("To be filled by O.E.M.", "").replace("To Be Filled By O.E.M.", "")

        try:
            _report["ram"] = root.find('.//Data[Элемент="Установленная оперативная память (RAM)"]/Значение').text
             # Определяем, какие единицы измерения содержит значение
            unit = "ГБ" if "ГБ" in  _report["ram"] else "МБ"
            
            # Удаляем единицы измерения из строки
            _report["ram"] = re.sub(r' МБ| ГБ', '',  _report["ram"])
            
            # Заменяем запятую на точку для корректной конверсации в число
            _report["ram"] = _report["ram"].replace(',', '.')
            # Преобразуем значение в число
            number = float(_report["ram"])
            
            # Если единица измерения была МБ, переводим в ГБ
            if unit == "МБ":
                number /= 1024  # Переводим МБ в ГБ
            
            # Округляем число до 1 десятичного знака и удаляем ненужный десятичный ноль, если возможно
            _report["ram"] = f"{number:.1f}"
            _report["ram"] = re.sub(r'\.0$', '', _report["ram"])  + " ГБ"
            


        except:
            _report["ram"] = root.find('.//Data[Элемент="Полный объем физической памяти"]/Значение').text
            _report["ram"] = _report["ram"].replace(',', '.')
            # _report["ram"] = re.sub(r'\s*МБ|\s+', '', _report["ram"]).replace(',', '.')
            # _report["ram"] = float(_report["ram"]) / 1024
            # _report["ram"] = f"{_report["ram"]:.1f} ГБ" if _report["ram"] % 1 != 0 else f"{int(_report["ram"])} ГБ"




        _report["hostname"] = root.find('.//Data[Элемент="Имя системы"]/Значение').text
        # try:
        #     #_report["motherboard"]["vendor"] = root.find('.//Data[Элемент="Изготовитель основной платы"]/Значение').text

        # except:
        #     pass
        # try:
        #     # _report["motherboard"]["model"] = root.find('.//Data[Элемент="Модель основной платы"]/Значение').text
        # except:
        #     pass
        
        
        arr_tmp_interface = []

        # Получение всех нужных данных за один проход
        adapter_types = root.findall('.//Category[@name="Адаптер"]/Data[Элемент="Тип адаптера"]/Значение')
        ip_addresses = root.findall('.//Category[@name="Адаптер"]/Data[Элемент="IP-адрес"]/Значение')
        mac_addresses = root.findall('.//Category[@name="Адаптер"]/Data[Элемент="MAC-адрес"]/Значение')

        # Заполнение массива интерфейсов
        for i in range(len(adapter_types)):
            adapter_type = adapter_types[i].text.split(",")[0].strip() if adapter_types[i].text else ""
            ip_address = ip_addresses[i].text.split(",")[0].strip() if i < len(ip_addresses) and ip_addresses[i].text else ""
            mac_address = mac_addresses[i].text.split(",")[0].strip() if i < len(mac_addresses) and mac_addresses[i].text else ""

            arr_tmp_interface.append([adapter_type, ip_address, mac_address])

        # Добавление данных в отчет
        for inter in arr_tmp_interface:
            if all(value != "Недоступно" for value in inter):
                _report["ip"].append(inter[1])
                _report["mac"].append(inter[2])

        print(arr_tmp_interface)



        try:
            _report["videoadapter"] = root.find('.//Category[@name="Дисплей"]/Data[Элемент="Описание адаптера"]/Значение').text
            _report["videoadapter"] = re.sub(r'\s\(.*?\)', '', _report["videoadapter"])
        except:
            pass

        try:
            _report["cd_dvd"] = root.find('.//Category[@name="CD-ROM"]/Data[Элемент="Имя"]/Значение').text 
            for word in ['CdRom Device','ATA Device','SCSI','USB Device', 'F']:
                if word in _report["cd_dvd"]:
                    _report["cd_dvd"] = _report["cd_dvd"].replace(word,"")
            _report["cd_dvd"] = _report["cd_dvd"].strip()
        except:
            pass

        data = root.findall('.//Category[@name="Диски"]')
        data = data[0]
        data = data.findall('.//Data/Значение')  

        counter = 10
        memorySize = 0
        for val in data:
            counter += 1
            if(val.text == "Local Fixed Disk" or val.text == "Локальный несъемный диск" or val.text == "Локальный жесткий диск"):
                counter = 0
            if(counter == 3):
                tmp = re.sub("\\(.*\\)","", val.text)
                tmp = tmp.strip()
                if(tmp[-3:] == " ГБ"):
                    tmp = tmp[:-3]
                    memorySize += float(tmp.replace(",", "."))
                elif(tmp[-3:] == " МБ"):
                    tmp = tmp[:-3]
                    memorySize += float(tmp.replace(",", ".")) / 1024
                elif(tmp[-3:] == " ТБ"):
                    tmp = tmp[:-3]
                    memorySize += float(tmp.replace(",", ".")) * 1024
                else:
                    pass
        _report["disk"] = str(int(memorySize)) + " ГБ"
        logger.info(f"Собран: {_path} \t\t {_report["hostname"]}")

        return _report
    except ET.ParseError:
        logger.error(f"Ошибка разбора NFO файла: {_path}")
        
        return None
    except FileNotFoundError:
        logger.error(f"Файл не найден: {_path}")
        
        return None
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке файла {_path}: {e}")
        return None

    
    

