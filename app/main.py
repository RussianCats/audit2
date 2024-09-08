# app/main.py
from app import *
from app.core import *
import pkg_resources


def main():
    parser = argparse.ArgumentParser(description="Приложение для анализа собранных данных с аудита")
    parser.add_argument("--name", help="Name of the user")
    parser.add_argument("--pathd", help="data path")
    args = parser.parse_args()
    
    # Используйте логгер через переменную logger
    logger.info("---------- START ----------")
    if args.name:
        print(f"Hello, {args.name}!")
        logger.info(f"Greeted user {args.name}")

    if args.pathd:
        config.CONFIG.EXECUTPATH = args.pathd
        # print(config.CONFIG.EXECUTPATH)

    config.CONFIG.LIBPATH = pkg_resources.resource_filename(__name__, '')


    logic()

    logger.info("---------- STOP ----------")

if __name__ == "__main__":
    main()

