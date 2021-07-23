# Бот для интернет-провайдера

Это проект демо-бота для управления функциями личного кабинета клиента интернет-провайдера:
- изменение тарифа
- оплата
- управление заморозкой


# Установка

Клонируйте репозиторий, и создайте виртуальное окружение. После этого установите зависимости:

```bash
$ pip install -r requirements.txt
```

## Переменные окружения

`SECRET_KEY` - Секретный ключ проекта.

`DEBUG` - Режим отладки. Установите 'False' для боевого режима.

`ALLOWED_HOSTS` - см [Django docs](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).

`DATABASE_URL` - Строка соединения с базой данных: "postgres://user:password@127.0.0.1:5432/database".


## Установка Postgres и Node-RED

Для установки сервисов требуется Docker.

```bash
$ docker-compose up
```

## Настройка Node-RED

Для запуска Node-red в корне проекта необходимо создать файл `node-red.env`
```
TZ=Europe/Moscow
TG_TOKEN=<токен телеграм-бота>
TG_BOT_NAME=<имя телеграм-бота>
TG_PAYMENT_TOKEN=<токен платежного провайдера телеграм>
NETUP_URL=<адрес API NETUP>
```
Открыть в браузере [Node-RED](http://127.0.0.1:1885/).

Поставить модули (Главное меню -> Управление палитрой -> Установить):
  - `node-red-contrib-chatbot`

## Создание и запуск проекта

Создание базы данных:

```bash
$ python manage.py migrate
```

Запуск сервера локально:

```bash
$ python manage.py runserver
```
