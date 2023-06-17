Foodgram
=====
![Foodgram](https://github.com/KVGribko/foodgram-project-react/actions/workflows/main.yml/badge.svg)

for review
----
host: http://51.250.103.223/
```
admin email: ad@ad.ru
admin username: ad
admin password: ad
```
Описание проекта
----------
Командный проект создан в рамках учебного курса Яндекс.Практикум.

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


Запуск проекта в Docker
----------

1. Подготовить удаленный сервер выполнив следующие команды:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
sudo systemctl stop nginx

sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
docker version
docker compose version

pip install gunicorn
sudo apt install nginx -y
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
sudo systemctl start nginx
sudo systemctl stop nginx

sudo docker image prune -a
```
2. Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone https://github.com/KVGribko/foodgram-project-react.git

cd foodgram-project-react
```
3. Скопировать на сервер файлы docker-compose.yml, nginx.conf
```bash
scp infra/docker-compose.yml infra/nginx.conf username@host:/home/username
```
4. Выполнить команду:
```bash
sudo docker compose up -d --build
```
5. Выполнить миграции:
```bash
sudo docker compose exec backend python manage.py migrate
```
6. Собрать статику:
```bash
sudo docker compose exec backend python manage.py collectstatic --no-input
```
7. Создать суперпользователя:
```bash
docker compose exec backend python manage.py createsuperuser
```
