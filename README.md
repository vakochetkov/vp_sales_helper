## vp_sales_helper

Небольшой telegram бот на [aiogram](https://github.com/aiogram/aiogram) и [aiohttp](https://github.com/aio-libs/aiohttp) ([полный список зависимостей](requirements.txt)) для уведомления сотрудников о новых заказах из [WooCommerce](https://woocommerce.com) с минимальным менеджментом заказов

* Присылает сообщение при появлении нового заказа на сайте магазина, упоминая нужных сотрудников на основе выбранного способа доставки
* Позволяет брать и завершать заказы (возможные статусы: новый, в обработке, завершен)
* Выводит время обработки заказа сотрудником
* **Не использует WooCommerce REST API или БД - нужен только настроенный webhook о новом заказе на URL `http://botserver.com:8080/wcapi/order`**

### Setup

**Необходимый минимум**: машина с статическим ip или привязанным доменом, чтобы установить webhook, docker для быстрого развертывания бота 

1. Скачать образ с Docker Hub `docker pull vakochetkov/vp_sales_helper` или собрать с Github `docker build -t vakochetkov/vp_sales_helper github.com/vakochetkov/vp_sales_helper`

2. При запуске установить PIN для команд, токен бота и адрес сервера через переменные среды `docker run -d --restart always --log-opt max-size=10m --log-opt max-file=2 -e VPSH_TOKEN="token" -e VPSH_ADMIN_PIN="pin" -e VPSH_SERVER="0.0.0.0" -e TZ=Europe/Berlin -p 8080:8080 vakochetkov/vp_sales_helper`

### Commands

##### /set_chat_{PIN} - установка рабочего чата с сотрудниками

*Формат:* 
`id чата`


*NB: бот должен быть добавлен в чат, чтобы иметь возможность присылать сообщения*


*NB: id чата можно получить, например, через @getidsbot*

##### /set_salers_{PIN} - установка новых настроек оповещения сотрудников

*Формат:*
`текст содержащиеся в названии типа доставки`
`username сотрудников через пробел`
*Пример:*
`Пушкинская`
`@vasya`
`Доставка почтой`
`@petya`
`Склад`
`@ilya @alex @petya`


*NB: для доставки неподходящей ни под одно поле выведется @everyone*

##### /get_config_{PIN} - вывод в human-readable формате текущих настроек