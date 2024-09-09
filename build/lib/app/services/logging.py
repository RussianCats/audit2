#app/services/logging.py
from app.services import *
from app.config import CONFIG
import time
import random

def generate_log_filename():
    # Получаем текущее время в формате ГГГГММДД_ЧЧММСС
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Генерируем 6 случайных чисел
    random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Формируем имя файла по шаблону
    filename = f"{timestamp}-{random_numbers}.log"
    
    CONFIG.NAMEFILELOG = filename
    return filename




# Создание логгера
logger = logging.getLogger('TAUDITV2')
logger.setLevel(logging.INFO)  # Установка уровня логирования

# Создание обработчика, который будет записывать логи в файл
file_handler = logging.FileHandler(f'log/{generate_log_filename()}')
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



