#!/bin/bash

REPO_URL="https://github.com/Asmin963/PskovEduBot"
REPO_NAME="PskovEduBot"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'


echo -e "${GREEN}Установка Python 3.11...${NC}"
sudo apt install -y python3.11 python3.11-dev python3.11-gdbm python3.11-venv
wget https://bootstrap.pypa.io/get-pip.py -nc
sudo python3.11 get-pip.py

rm -rf get-pip.py

echo -e "${GREEN}Установка git...${NC}"
sudo apt install -y git

sudo rm -rf PskovEduBot

echo -e "${GREEN}Клонирование репозитория PskovEduBot...${NC}"
git clone $REPO_URL"

echo -e "${GREEN}Создаю виртуальное окружение и устанавливаю зависимости...${NC}"
cd PskovEdutBot
pip install -r reqierements.txt

echo -e "${GREEN}Установка pm2...${NC}"
npm install -g pm2

echo -e "${GREEN}Запускаю PskovEdutBot${NC}"
pm2 start main.py --interpreter python3.11 --name PskovEduBot

pm2 save

pm2 startup

echo -e "${CYAN}Установка завершена!${NC}"
