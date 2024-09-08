# app/main.py
from app import *
from app.core import *
from pathlib import Path
import pkg_resources
import shutil

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
    print(config.CONFIG.LIBPATH)

    logic()

    logger.info("---------- STOP ----------")

    
    # копируем лог
    libpath = Path(config.CONFIG.LIBPATH)
    shutil.copy(libpath.parent / "log" / Path(config.CONFIG.NAMEFILELOG), Path(config.CONFIG.EXECUTPATH))

    
if __name__ == "__main__":
    main()

