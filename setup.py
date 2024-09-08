from setuptools import setup, find_packages

# Чтение списка зависимостей из файла requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='my_console_app',
    version='1.0',
    packages=find_packages(),
    install_requires=required,  # Использование списка зависимостей
    entry_points={
        'console_scripts': [
            'taudit2=app.main:main',
        ],
    },
)
