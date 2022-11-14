# python advanced (skillbox)

дипломный проект по курсу python advanced от skillbox

## быстрый старт
* рядом с docker-compose положить файл .env и переопределить переменные. Пример можно взять в default.env
* создать папку для хранения данных на хост-машине, присвоить ей права 777

Запуск всего зоопарка:
```shell
docker-compose -f docker-compose.deploy.yml up -d --build
```

# внешний доступ к контейнерам
* http://127.0.0.1:7200 - frontend
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

* метрики
  * grafana
  * prometheus

# elasticsearch + kibana-mother
Нужно зайти в кибану и настроить получение логов с fluentd проекта. add intergations - discover - add data source

#grafana
Добавить dashboards по вкусу. Рекомендую:
* 