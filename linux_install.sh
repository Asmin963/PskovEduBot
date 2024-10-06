#!/bin/bash

REPO_URL="https://github.com/Asmin963/PskovEduBot"
REPO_NAME="PskovEduBot"

echo "Клонирую репозиторий..."
git clone "$REPO_URL"

cd "$REPO_NAME" || exit

echo "Создаю виртуальное окружение и устанавливаю зависимости..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Установка pm2..."
npm install -g pm2

echo "Запуск main.py через pm2..."
pm2 start main.py --interpreter python3 --name your-app-name

pm2 save

pm2 startup

echo "Установка завершена!"
