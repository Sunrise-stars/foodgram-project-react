# praktikum_new_diplom


# Foodgram - социальная сеть о кулинарии
### Делитесь рецептами и пробуйте новые 🍰
---
### Сервис доступен по адресу:

``http://myfood.serveblog.net``


### Возможности сервиса:
- делитесь своими рецептами
- смотрите рецепты других пользователей
- добавляйте рецепты в избранное
- быстро формируйте список покупок, добавляя рецепт в корзину
- следите за своими друзьями и коллегами

### Технологии:
- Django
- Python
- Docker

### Запуск проекта:

```
1. Подготовьте сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/
```
2. Установите docker и docker-compose:
```
sudo apt install docker.io 
sudo apt install docker-compose
```
3. Соберите контейнер и выполните миграции:
```
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py migrate
```
4. Создайте суперюзера и соберите статику:
```
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
5. Скопируйте предустановленные данные json:
```
sudo docker-compose exec backend python manage.py loadmodels --path 'recipes/data/ingredients.json'
sudo docker-compose exec backend python manage.py loadmodels --path 'recipes/data/tags.json'
```
6. Данные для проверки работы приложения:
Суперпользователь:
```
**Admin**

**Username** ``AdminTrial@test.test``

**Password** ``qweqweqwe``
```

