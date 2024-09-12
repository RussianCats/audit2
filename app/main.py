from app.services.logging import setup_logging
from app.config import CONFIG
from app.core import logic
import argparse
import pkg_resources

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

    # Теперь инициализируем логирование после установки CONFIG.EXECUTPATH и CONFIG.LIBPATH
    logger = setup_logging()

    if args.name:
        print(f"Hello, {args.name}!")
        logger.info(f"Greeted user {args.name}")

    logger.info("---------- START ----------")
    
    # Запуск основной логики
    logic()

    logger.info("---------- STOP ----------")

if __name__ == "__main__":
    main()
