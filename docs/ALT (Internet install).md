Система администрирования ЛПУ
=================

Для установки системы администрирования ознакомьтесь с техническими требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* ОС ALTLinux

### Необходимое ПО, поставляемое с дистрибутивом ALTLinux

* Python 2.7
* Web-Server Apache2 + apache2-mod_wsgi
* zlib

### Устанавливаемое ПО

**Update системы**

```
apt-get update
apt-get upgrade
```

* C-compiler (gcc) ```apt-get install gcc4.5``` (установить подходящую версию, в указанном случае gcc4.5)
* СУБД
 * MySQL 5 (MySQL-server, MySQL-client) ```apt-get install MySQL-server``` ```apt-get install MySQL-client```
   * python-module-MySQLdb ```apt-get install python-module-MySQLdb```
 * или
 * PostgreSQL ```apt-get install postgresql-server postgresql-client postgresql-contrib``` (руководство по первоначальной установке PostgreSQL можно найти в Интернете)
* python-module-MySQLdb ```apt-get install python-module-MySQLdb```
* libxml2-devel ```apt-get install libxml2-devel```
* libxslt-devel ```apt-get install libxslt-devel```
* libmysqlclient-devel ```apt-get install libmysqlclient-devel```
* zlib-devel ```apt-get install zlib-devel```

**Пакеты для установки из Интернета**

* git ```apt-get install git```
* python-module-setuptools ```apt-get install python-module-setuptools```


Установка
-----------

Описанная ниже установка и настройка ПО производится из консоли Linux. Используется root-доступ.


### Перенос исходников на сервер

Используем директорию /srv/ для обеспечения защищенной установки. Вместо /srv можно использовать любую удобную директорию на сервере (например, /var/www/webapps).

При этом, следуя инструкции, необходимо подразумевать, что вместо /srv необходимо указывать Вашу директорию.

В качестве имени проекта (my_project) можно использовать произвольное.

```
cd /srv/my_project
git clone https://github.com/KorusConsulting/Caesar.git code
```
при этом необходимо наличие github аккаунта с правами доступа в корпоративный репозиторий

**Если доступа к репозиторию нет, но есть архив с исходниками проекта - достаточно распаковать его в отведенную директорию.**


### Установка fabric для автоматического развёртывания проекта

```
easy_install fabric
```

Настройка конфига
-----------

Переименовать файл config_local.py_mysql (для MySQL-версии) или config_local.py_psql (для PostgreSQL-версии) в config_local.py и заменить в нем значения настроек на актуальные, например:

```
#Параметры подключения к БД
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'caesar'
DB_PASSWORD = 'q1w2e3r4t5'
DB_NAME = 'caesar'

#Системный пользователь, от которого будет запускаться вэб-сервер
SYSTEM_USER = 'caesar'

#Хост и порт, по которым будет доступна система
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
```

**Автоматическая установка**

```
fab deploy
```

В процессе установки может потребоваться ввести логин/пароль администратора MySQL, из-под которого будет создан пользователь БД.

Настройка системы
-----------

При установке системы автоматически создаётся два аккаунта:
* Администратора (Логин: admin / Пароль: admin)
* Пользователя (Логин: user / Пароль: user)

* Зайти в интерфейс настроек, залогинившись под администратором:
http://%SERVER_HOST%:%SERVER_POR%T/settings/

И заполнить значения конфигурационных параметров.

В каждом из модулей в настройках необходимо прописать адрес соответствующего вэб-сервиса в ядре, а также задать конфигурационные значения.

В настройки модуля можно попасть из меню модуля.
