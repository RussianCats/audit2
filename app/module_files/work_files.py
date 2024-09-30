#app/module_files/work_files.py
from app import *
import re
import chardet
from pathlib import Path
from app.services.logging import setup_logging
from app.module_parse.tools_json import *
logger = setup_logging()




# считывание файла построчно
def readFileToList(_file_path):
    try:

        data_list = []
        with open(_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                    data_list.append([str(line.replace('\n', '')
                                          .replace("\xa0", " ")), True])
        return data_list
    except FileNotFoundError:
        logger.error(f"Файл {_file_path} не найден.")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {_file_path}: {e}")
        return []


# считывание файла отчета txt
def readReportTXTFile(_file_path, _report, _boolAddres=False):
    # Получить адрес
    if _boolAddres:
        pathAddr = Path(_file_path)
        if len(pathAddr.parts) > 3:  # Убедитесь, что в пути достаточно компонентов
            _report["org"]["address"] = pathAddr.parts[-3]
        else:
            _report["org"]["address"] = ""

    # Считываем байты из файла для определения кодировки
    with open(_file_path, 'rb') as raw_data:
        result = chardet.detect(raw_data.read())
        encoding = result['encoding']

    # Открываем файл в определенной кодировке
    with open(_file_path, 'r', encoding=encoding) as file:
        for line in file:
            # Очистка строки от пробелов и перевода строки
            clean_line = line.strip()
            # Разбиение строки на ключ и значение
            parts = clean_line.split(':', 1)
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                # Определение ключа и запись значения в _report
                if key == "hostname":
                    _report["hostname"] = value
                elif key == "monitor":
                    _report["monitor"] = re.split(r'\s*[;,/]\s*', value)  
                elif key == "keyboard":
                    _report["keyboard"] = value
                elif key == "mouse":
                    _report["mouse"] = value
                elif key == "inventory":
                    _report["org"]["inventory"] = value
                elif key == "cabinet":
                    _report["org"]["cabinet"] = value
                elif key == "structural":
                    _report["org"]["structural"] = re.split(r'\s*[;,]\s*', value)  
                elif key == "worker":
                    _report["org"]["FIO"] = re.split(r'\s*[;,/]\s*', value)  
                elif key == "uuid":
                    _report["uuid"] = value 
                      
            else:
                logger.error(f"Некорректная строка: {clean_line}. Файл: {_file_path}")

        # if (_report["uuid"] == ""):
        #     print(f"!!!!!!!!!!{_report["hostname"]}")  

    return _report



# считывание файловой системы по папке 
def readDir(_path):
    directory_path = Path(_path) 
    paths = []

    # Используем rglob для поиска всех файлов в директории и поддиректориях
    for file_path in directory_path.rglob('*'):
        # Проверяем, является ли путь файлом (в противном случае это может быть поддиректория)
        if file_path.is_file():
            paths.append(file_path)
    return(paths)
