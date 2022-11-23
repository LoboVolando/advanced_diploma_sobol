# python advanced (skillbox)

дипломный проект по курсу python advanced от skillbox

## структура проекта
* **sphinx-docs** - автодокументация кода
* **frontend** - Клиентская частьь проекта для контейнера, в нём же конфигурируется проксирующий сервер nginx
* **backend** - Серверной часть проекта для контейнера.
* **fluentd** - Настройки контейнера логгирования.
* **elasticsearch** - Настройки сервиса логгирования.
* **kibana** - настройки сервиса поиска по логам.
* **prometheus** - настройки сервиса сбора метрик.
* **grafana** - настройки интерфейса для сервиса метрик.
* **postgres_exporter** - настройки экспортера метрик для контейнера с базой данных.
* **.gitlab-ci.yml, fabfile.py** - настройки непрерывной интеграции и развёртывания проекта.
* **Makefile** - автоматизация некоторых процессов
* **pyproject,toml, setup.cfg** - конфигурация проекта
* **requirements.txt** - файл зависимостей для серверной части проекта.
* **readme.md** - вы находитесь здесь.
* **docker-compose.*.yml** - файл конфигурации для запуска проекта.

## структура контейнеров
* **frontend** - контейнер с клиентской частью. 
* **backend** - контейнер с серверной частью.
* **postgres** - контейнер СУБД.
* **pgadmin** - контейнер с админкой СУБД.
* **prometheus** - контейнер сбора метрик.
* **grafana** - контейнер с интерфейсом сервиса сбора метрик.
* **node-exporter** - экспортер метрик о нагрузке железной части сервера.
* **nginx-exporter** - экспортер метрик о нагрузке на проксирующий сервер. 
* **postgres-exporter** - экспортер метрик СУБД.
* **cadvisor** - экспортер метрик для запущенных контейнеров.
* **elasticsearch** - контейнер сбора логов.
* **kibana** - интерфейс сервиса сбора логов.
* **fluentd** - контейнер аггрегирует логи контейнеров и отправляет elasticsearch

## настройка проекта
Для успешного запуска нужно настроить переменные для docker-compose. Сделать это можно, например, подложив рядом файл ```.env```
В файле нужно определить следующие переменные:
```
ELK_VERSION=8.4.3
ELASTIC_PASSWORD=ElasticPassword
DATA_ROOT=/home/svv/data/diploma
SERVER_MEDIA_ROOT=/home/svv/data/diploma/static/media
DOCKER_MEDIA_ROOT=/static/media
POSTGRES_ROOT_PASSWORD=PostgresPassword
POSTGRES_ROOT_USER=postgres
POSTGRES_ROOT_DB=postgres
PGADMIN_DEFAULT_PASSWORD=PgAdminPassword
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
MEDIA_URL=/static/media
NGINX=./frontend/nginx.conf
ALEMBIC=alembic_production.ini
DEBUG=false
```
**Внимание, папка для переменной ```DATA_ROOT``` должна иметь права 777, иначе некоторые контейнеры не смогут писать в неё данные**
```sudo chown -R 777 .```


##Запуск контейнеров:
```shell
docker-compose -f docker-compose.deploy.yml up -d --build
```
##Остановка контейнеров:
```shell
docker-compose -f docker-compose.deploy.yml down
```
##Просмотр логов контейнеров:
```shell
docker-compose -f docker-compose.deploy.yml logs [имя сервиса]
```

# внешний доступ к контейнерам
* http://127.0.0.1:7200 - frontend
* http://127.0.0.1:7200/api/docs - документация swagger
* http://127.0.0.1:7202 - backend
* http://127.0.0.1:7204 - pgadmin
* http://127.0.0.1:7203 - grafana. admin:admin - и не забыть поменять пароль
* http://127.0.0.1:7209 - prometheus
* http://127.0.0.1:7215 - elasticsearch
* http://127.0.0.1:7220 - kibana

# ci/cd
  * установить gitlab-runner на сервер и зарегистрировать его. В настройках гитлаб отключить использование теневых раннеров
  * подкинуть в папку /home/gitlab-runner/.ssh файлики:
    * authorized-keys
    * id_rsa
    * id_rsa.pub
    * know-hosts
  * выполнить:

```shell
sudo chown gitlab-runner:gitlab-runner *
sudo usermod -aG docker gitlab-runner
```
  * выполнить ещё какую-то команду, чтобы гит не сомневался, что в этой папке всё хорошо

# elasticsearch + kibana-mother
В кибана следует настроить получение логов с fluentd проекта. add intergations - discover - add data source

#grafana
Добавить dashboards по вкусу.