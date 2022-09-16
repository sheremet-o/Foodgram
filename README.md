# Данные для проверки

Адрес сайта  
<http://158.160.4.225/>

Администратор:  
email: foodgram@mail.ru  
login: foodgram  
password: foodgram  

Обычный пользователь:  
email: user1@mail.ru  
login: user1  
password: andreevuser1  

## Описание

Foodgram - «продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стек технологий

* Python 3.8.5
* Django 2.2.16
* Django Rest Framework 3.12.14
* Simple JWT 4.8.0
* gunicorn 20.0.4
* Docker 20.10.6
* docker-compose 1.25.0
* Nginx 1.19.3
* Postgres 12.4

## Запуск приложения в контейнере

1. Запустите docker-compose при помощи команды  
`docker-compose up -d`
2. Соберите статические файлы (статику):  
`docker-compose exec backend python manage.py collectstatic --no-input`
3. Примените миграции:  
`docker-compose exec backend python manage.py makemigrations`
`docker-compose exec backend python manage.py migrate --no-input`
4. Создайте суперпользователя:  
`docker-compose exec backend python manage.py createsuperuser`
5. При необходимости наполните базу тестовыми данными из backend/data/:  
`docker-compose exec backend python manage.py load_ingredients`
6. Запустите приложение  
`docker-compose exec backend python manage.py runserver`

## Аутентификация и создание новых пользователей  

Получение токена (POST).  
`api/auth/token/login/`

## Алгоритм регистрации пользователей

1. Пользователь отправляет POST-запрос для регистрации нового пользователя с параметрами email username first_name last_name password на эндпойнт /api/users/
2. Пользователь отправляет POST-запрос со своими регистрационными данными email password на эндпоинт /api/token/login/ , в ответе на запрос ему приходит auth-token.

## Набор доступных эндпоинтов

 `api/docs/redoc` - Подробная документация по работе API.  
 `api/tags/` - Получение, списка тегов (GET).
 `api/ingredients/` - Получение списка ингредиентов (GET).  
 `api/ingredients/` - Получение ингредиента с соответствующим id (GET).  
 `api/tags/{id}` - Получение тега с соответствующим id (GET).  
 `api/recipes/` - Получение списка с рецептами и публикация рецептов (GET, POST).  
 `api/recipes/{id}` - Получение, изменение, удаление рецепта с соответствующим id (GET, PUT, PATCH, DELETE).  
 `api/recipes/{id}/shopping_cart/` - Добавление рецепта с соответствующим id в список покупок и удаление из списка (GET, DELETE).  
 `api/recipes/{id}/favorite/` - Добавление рецепта с соответствующим id в список избранного и его удаление (GET, DELETE).  

## Операции с пользователями

 `api/users/` - получение информации о пользователе и регистрация новых пользователей. (GET, POST).  
 `api/users/{id}/` - Получение информации о пользователе. (GET).  
 `api/users/me/` - получение и изменение данных своей учётной записи. Доступна любым авторизованными пользователям (GET).  
 `api/users/set_password/` - изменение собственного пароля (PATCH).  
 `api/users/{id}/subscribe/` - Подписаться на пользователя с соответствующим id или отписаться от него. (GET, DELETE).  
 `api/users/subscribe/subscriptions/` - Просмотр пользователей на которых подписан текущий пользователь. (GET).  

## Ближайшие обновления

Hастройка workflow
