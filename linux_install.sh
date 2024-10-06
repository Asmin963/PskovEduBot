#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${GREEN}Установка Python 3.12 и зависимостей...${NC}"
sudo apt install -y python3.12 python3.12-dev python3.12-gdbm python3.12-venv
wget https://bootstrap.pypa.io/get-pip.py -nc
sudo python3.12 get-pip.py

rm -rf get-pip.py

echo -e "${GREEN}Установка git...${NC}"
sudo apt install -y git

sudo rm -rf FunPayCardinal

echo -e "${GREEN}Клонирование репозитория PskovEduBot...${NC}"
git clone https://github.com/Asmin963/PskovEduBot

echo -e "${GREEN}Переход в директорию проекта...${NC}"
cd PskovEduBot  

echo -e "${GREEN}Создаю виртуальное окружение и устанавливаю зависимости...${NC}"
pip install -r reqierements.txt

echo -e "${GREEN}Установка pm2...${NC}"
npm install -g pm2

echo -e "${GREEN}Запуск main.py через pm2...${NC}"
pm2 start main.py --interpreter python3.12 --name PskovEduBot

pm2 save

pm2 startup

echo -e "${GREEN}Установка завершена!${NC}"
