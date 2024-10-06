#!/bin/bash

REPO_URL="https://github.com/Asmin963/PskovEduBot"
REPO_NAME="PskovEduBot"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

set -e

echo -e "${CYAN}Установщик PskovEduBot${NC}"

echo -e "${GREEN}Обновление пакетов...${NC}"
sudo apt update -y && sudo apt upgrade -y

echo -e "${GREEN}Установка языкового пакета...${NC}"
sudo apt install -y language-pack-ru

echo -e "${GREEN}Проверка локалей...${NC}"
if ! locale -a | grep -q 'ru_RU.utf8'; then
    echo -e "${GREEN}Обновление локалей...${NC}"
    sudo update-locale LANG=ru_RU.utf8

    echo -e "${RED}Локали ещё не установлены. Пожалуйста, перезапустите терминал и повторите команду запуска скрипта.${NC}"
    exit 1
fi

cd ~

echo -e "${GREEN}Установка Python 3.11 и зависимостей...${NC}"
sudo apt install -y python3.11 python3.11-dev python3.11-gdbm python3.11-venv
wget https://bootstrap.pypa.io/get-pip.py -nc
sudo python3.11 get-pip.py
pip install -e reqietements.txt

rm -rf get-pip.py

echo -e "${GREEN}Установка git...${NC}"
sudo apt install -y git

sudo rm -rf PskovEduBot

echo -e "${GREEN}Клонирование репозитория PskovEduBot...${NC}"
git clone $REPO_URL"

echo -e "${GREEN}Создаю виртуальное окружение и устанавливаю зависимости...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo -e "${GREEN}Установка pm2...${NC}"
npm install -g pm2

echo -e "${GREEN}Запускаю PskovEdutBot${NC}"
pm2 start main.py --interpreter python3 --name PskovEduBot

pm2 save

pm2 startup

echo -e "${CYAN}Установка завершена!${NC}"
