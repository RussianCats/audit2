from app import *
from collections import OrderedDict
import json



def logic():
    # список фсех файлов в указанной папке
    _path_FullFiles = work_files.readDir(Path(config.CONFIG.EXECUTPATH) / "database")

    _list_report = []

    # считываем орг данные из ексель таблиц
    for xlsx_file in [file for file in _path_FullFiles if file.suffix == '.xlsx']:
        _list_report.extend(exel.readExcelFile(xlsx_file, CONFIG.SIZE_TABLE))
    
    # считываем орг данные из txt файлов 
    for txt_file in [file for file in _path_FullFiles if file.suffix == '.txt']:
        _list_report.append((work_files.readReportTXTFile(txt_file, deepcopy(infoReport), False)))

    # считываем орг и тех данные из json файлов, потому что они содержать в себе все
    _list_reportJSON = []
    for json_file in [file for file in _path_FullFiles if file.suffix == '.json']:
        _list_reportJSON.append(module_parse.tools_json_linux.parseJSONLinux(json_file))
    _list_reportJSON = [i for i in _list_reportJSON if i is not None]
    _list_report += _list_reportJSON
        
    # удаляем дубликаты орг части
    _list_report = delDuplicateReport(_list_report)


    # считываем отчеты с xml
    _list_reportXML = []
    for xml_file in [file for file in _path_FullFiles if file.suffix == '.xml']:
        _list_reportXML.append(module_parse.tools_xml.parseXML(xml_file))
    _list_reportXML = [i for i in _list_reportXML if i is not None]


    # считываем отчеты с nfo
    _list_reportNFO = []
    for nfo_file in [file for file in _path_FullFiles if file.suffix == '.nfo']:
        _list_reportNFO.append(module_parse.tools_nfo.parseNFO(nfo_file))
    _list_reportNFO = [i for i in _list_reportNFO if i is not None]

    # объединяем орг и тех часть из xml и nfo отчетов
    _list_report = merge_reports(_list_report, _list_reportXML + _list_reportNFO)

    
    # нахождение одинаковых сетевых имен и инвентарников для добавления дополнительной информации
    _list_report = findRepHostnameAndInventory(_list_report)

    # чистка данных
    _list_report = clenDataReport(_list_report)

    # запись данных в таблицу
    exel.writeExelTable(_list_report)






def delDuplicateReport(_listReports):
    unique_reports = OrderedDict()

    # Счётчик дубликатов для логирования
    duplicate_count = 0

    for report in _listReports:
        # Создаём уникальный ключ для каждого отчёта
        unique_key = (
            report["uuid"],
            report["org"]["address"],
            tuple(report["org"]["structural"]),
            report["org"]["cabinet"],
            tuple(report["org"]["FIO"]),
            report["hostname"].upper(),
            report["org"]["inventory"],
            tuple(report["monitor"]),
            report["keyboard"],
            report["mouse"]
        )

        # Сохраняем только первое вхождение для каждого уникального ключа
        if unique_key not in unique_reports:
            unique_reports[unique_key] = report
        else:
            duplicate_count += 1
            logger.warn(f"Найден дубликат: {report["hostname"]}")

    logger.info(f"Чистим от дубликатов, найдено {duplicate_count} дубликатов")
    return list(unique_reports.values())


# ОБЪЕДИНЯЕТ ДАННЫЕ С ОТЧЕТОВ И ОРГДАННЫМИ при условии 
# 1) одинаковом uuid и hostname 
# 2) только hostname если в оргданных нет uuid
def merge_reports(_list_report, _list_reportTech):
    # Обходим элементы массива _list_reportTech
    for reportXML in _list_reportTech:
        # Получаем обрезанный uuid и hostname текущего элемента из _list_reportTech
        uuid = reportXML["uuid"].split('-')[0]
        hostname = reportXML["hostname"].upper()

        # Переменная для отслеживания существования элемента в _list_report
        foundTech = False

        # Обходим элементы массива _list_report
        for report in _list_report:
            # Проверяем, является ли uuid в report пустым
            if report["uuid"] == None:
                # Если uuid пустой, сравниваем только по hostname
                if report["hostname"].upper() == hostname:
                    foundTech = True
            else:
                # Если uuid не пустой, сравниваем по обоим параметрам
                if report["uuid"].split('-')[0] == uuid and report["hostname"].upper() == hostname:
                    foundTech = True

            # Если нашли совпадение, обновляем информацию в report
            if foundTech:
                report["uuid"] = reportXML["uuid"]
                report["ip"] = reportXML["ip"]
                report["mac"] = reportXML["mac"]
                report["cpu"] = reportXML["cpu"]
                report["videoadapter"] = reportXML["videoadapter"]
                report["cd_dvd"] = reportXML["cd_dvd"]
                report["motherboard"] = reportXML["motherboard"]
                report["os"] = reportXML["os"]
                report["ram"] = reportXML["ram"]
                report["disk"] = reportXML["disk"]
                report["ipt_list"] = reportXML["ipt_list"]
                report["app_list"] = reportXML["app_list"]
                break  # Прекращаем поиск, так как нужный элемент найден

        # Если элемент не найден, добавляем его в _list_report
        if not foundTech:
            if not CONFIG.DELL_ARM_NOT_FIND_ORG:
                _list_report.append(reportXML)
            logger.error(f"Не найдены ОРГ данные для АРМ - host: {reportXML["hostname"]}")
            

    # костыль, надо исправить
    for report in _list_report:
        if(report["os"]["small"] == "" and (report["cpu"] == "" or report["motherboard"]["vendor"] == "")):
            logger.error(f"Не найдены ТЕХ данные для АРМ - host: {report["hostname"]}")

    logger.info(f"Произошло объединение оргданных с техданными")
    return _list_report

# ищет АРМ с одинаковым сетевым именем или инвентарников (в условиях когда инвентартник б/н), чтобы добавить условия повторяющихся 
def findRepHostnameAndInventory(_list_report):
    # Создаем словарь для отслеживания дубликатов
    seen = {}

    # Проходим по каждому элементу в списке
    for item in _list_report:
        # Формируем ключ из hostname и inventory
        key = (item['hostname'].upper(), item['org']['inventory'])

        # Проверяем, если такой ключ уже есть в словаре
        if key in seen:
            # Устанавливаем duplicate в true для текущего и предыдущего элементов, которые были помечены как виденные
            item['duplicate'] = 'true'
            for prev_item in seen[key]:
                prev_item['duplicate'] = 'true'
            seen[key].append(item)
        else:
            seen[key] = [item]
    logger.info(f"Найдены ARM с одинаковыми сетевыми именами")
    return _list_report


def clenDataReport(_list_report):

    osClean = [
        "Microsoft Windows 11 Pro",
        "Microsoft Windows 10 Home", 
        "Microsoft Windows 10 Enterprise", 
        "Microsoft Windows 10 Education",
        "Microsoft Windows 10 Pro", 
        "Microsoft Windows 8.1 Pro", 
        "Microsoft Windows 7 Home", 
        "Microsoft Windows 7 Professional", 
        "Microsoft Windows Server 2012", 
        "Microsoft Windows Server 2016",
        "Microsoft Windows XP Professional",
        "Microsoft Windows Server 2008"
            ]

    # Словарь замен
    replacements = {
        "Майкрософт": "Microsoft",
        "Домашняя базовая": "Home Basic",
        "Домашняя расширенная": "Home Extended",
        "Профессиональная": "Professional",
        "Корпоративная": "Enterprise "
    }

    for report in _list_report:
        # для ОС
        # Получаем текущее значение
        current_os = report["os"]["small"]

        # Проходим по словарю замен и выполняем замены в строке
        for old, new in replacements.items():
            current_os = current_os.replace(old, new)


        for clean_os in osClean:
            if clean_os in current_os:
                report["os"]["small"] = clean_os
                break  # Прерываем внутренний цикл, так как замена уже произведена

        # изменение инвентарника на б/н
        if CONFIG.CHANGE_INVENTORY and (report["org"]["inventory"] == "" or report["org"]["inventory"] == "-"):
            report["org"]["inventory"] = "б/н"

        # изменение наименования монитора клавиатуры и мыши оставляя только модель
        if CONFIG.CHANGE_ONLY_VENDOR_FOR_PERIPHERY:

            report["monitor"] = [k.strip().split(" ")[0] for k in report["monitor"] if k.split(" ")]
            report["mouse"] = report["mouse"].strip().split(" ")[0]
            report["keyboard"] = report["mouse"].strip().split(" ")[0]
           
    logger.info(f"Процесс отчистки данных отчетов от мусора")
    return _list_report


        
