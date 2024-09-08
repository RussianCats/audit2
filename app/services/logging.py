
#app/services/logging.py
from app.services import *

# Создание логгера
logger = logging.getLogger('TAUDITV2')
logger.setLevel(logging.INFO)  # Установка уровня логирования

# Создание обработчика, который будет записывать логи в файл
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# Создание обработчика вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Например, выводить в консоль только ошибки

# Создание и установка форматтера
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)



