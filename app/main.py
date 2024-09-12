from app.services.logging import setup_logging
from app.config import CONFIG
from app.core import logic
from pathlib import Path
import argparse
import pkg_resources
import shutil
import os

def main():
    # Создание парсера аргументов
    parser = argparse.ArgumentParser(description="Приложение для анализа собранных данных с аудита")
    parser.add_argument("--name", help="Name of the user")
    parser.add_argument("--pathd", help="data path")
    args = parser.parse_args()

    # Установка путей в CONFIG до инициализации логгера
    if args.pathd:
        CONFIG.EXECUTPATH = args.pathd
    else:
        print("Нет пути --pathd")
        exit()

    CONFIG.LIBPATH = pkg_resources.resource_filename(__name__, '')
    print

    logger = setup_logging()

    if args.name:
        print(f"Hello, {args.name}!")
        logger.info(f"Greeted user {args.name}")

    logger.info("---------- START ----------")
    
    # Запуск основной логики
    logic()

    logger.info("---------- STOP ----------")

    # Пути из вашего конфигурационного файла
    source_file = Path().resolve() / CONFIG.NAMEFILELOG
    destination_dir = Path(CONFIG.EXECUTPATH)

    # Проверяем, существует ли директория назначения
    if destination_dir.exists():
        destination_file = destination_dir / CONFIG.NAMEFILELOG
        
        # Копирование файла
        shutil.copy(source_file, destination_file)
        print(f"Файл лога {CONFIG.NAMEFILELOG} успешно скопирован в папку пользователя")
        
        # Завершаем работу всех обработчиков логгера
        for handler in logger.handlers[:]:
            handler.close()       # Закрываем обработчик
            logger.removeHandler(handler)  # Убираем его из логгера
        
        # Удаление файла после успешного копирования
        try:
            source_file.unlink()  # Удаление через pathlib
            print(f"Файл лога {CONFIG.NAMEFILELOG} успешно удален из исходной директории")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
    else:
        print(f"Файл лога {CONFIG.NAMEFILELOG} не скопирован в папку пользователя")

    
if __name__ == "__main__":

    
    main()
