Система администрирования ЛПУ
=================

Для установки системы администрирования ознакомьтесь с техническими требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* ОС AltLinux

### Необходимое ПО, поставляемое с дистрибутивом AltLinux

* Python 2.7
* Web-Server Apache2 + apache2-mod_wsgi
* zlib

### Устанавливаемое ПО

**Update системы**

```
apt-get update
apt-get upgrade
```

* C-compiler (gcc) ```apt-get install gcc4.4``` (установить подходящую версию, в данном случае 4.4)
 * binutils
 * cpp4.4
 * gcc-common
 * glibc
 * glibc-devel
 * glibc-kernheaders
 * glibc-timezones
 * kernel-headers-common
 * libmprf
 * tzdata
* СУБД
 * MySQL 5 (MySQL-server, MySQL-client) ```apt-get install MySQL-server``` ```apt-get install MySQL-client```
   * python-module-MySQLdb ```apt-get install python-module-MySQLdb```
 * или
 * PostgreSQL ```apt-get install postgresql-server postgresql-client postgresql-contrib``` (руководство по первоначальной установке PostgreSQL можно найти в Интернете)
* libxml2-devel ```apt-get install libxml2-devel```
* libxslt-devel ```apt-get install libxslt-devel```
 * libxslt
* libmysqlclient-devel ```apt-get install libmysqlclient-devel```
* zlib-devel ```apt-get install zlib-devel```


**Во вложенных пунктах указаны зависимости, которые потребуется разрешить**


Установка
-----------

Описанная ниже установка и настройка ПО производится из консоли Linux. Используется root-доступ.


### Установка и настройка виртуального окружения, библиотек Python

```
apt-get install python-module-virtualenv
```
(https://pypi.python.org/pypi/virtualenv)

Используем директорию /srv/ для обеспечения защищенной установки. Вместо /srv можно использовать любую удобную директорию на сервере (например, /var/www/webapps).

При этом, следуя инструкции, необходимо подразумевать, что вместо /srv необходимо указывать Вашу директорию.

В качестве имени проекта (my_project) можно использовать произвольное.

```
cd /srv/my_project
```

#### Установка python-модулей в виртуальное окружение

**Создание и активация виртуального окружения**

```
virtualenv .virtualenv
source .virtualenv/bin/activate
```

**Общий принцип установки python-модулей**

* Заливаем во временную директорию (например /srv/my_project/tmp) архив модуля, скаченный с https://pypi.python.org/
* Распаковываем архив и переходим в директорию модуля
 * ```tar xvfz *.tar.gz``` или ```unzip *.zip```
 * ```cd unpacked_module_dir```
* Выполняем ```python setup.py install```

**Перечень модулей для установки**

* distribute (https://pypi.python.org/pypi/distribute/)
* setuptools (https://pypi.python.org/pypi/setuptools/)
* lxml (https://pypi.python.org/pypi/lxml/)
* Модуль для работы с СУБД:
 * mysql-python (https://pypi.python.org/pypi/MySQL-python/) - для MySQL
 * или
 * psycopg2 (https://pypi.python.org/pypi/psycopg2/) - для PostgreSQL
* MarkupSafe (https://pypi.python.org/pypi/MarkupSafe/)
* Mako (https://pypi.python.org/pypi/Mako/)
* itsdangerous (https://pypi.python.org/pypi/itsdangerous/)
* fabric (https://pypi.python.org/pypi/Fabric/)
 * pycrypto (https://pypi.python.org/pypi/pycrypto/)
 * paramiko (https://pypi.python.org/pypi/paramiko/)
* Flask (https://pypi.python.org/pypi/Flask/)
 * Jinja2 (https://pypi.python.org/pypi/Jinja2/)
 * Werkzeug (https://pypi.python.org/pypi/Werkzeug/)
* WTForms (https://pypi.python.org/pypi/WTForms/)
* Flask-WTF (https://pypi.python.org/pypi/Flask-WTF/)
* Flask-Admin (https://pypi.python.org/pypi/Flask-Admin/)
* Flask-BabelEx (https://pypi.python.org/pypi/Flask-BabelEx/)
 * speaklater (https://pypi.python.org/pypi/speaklater/)
 * pytz (https://pypi.python.org/pypi/pytz/)
 * Babel (https://pypi.python.org/pypi/Babel/)
* SQLAlchemy (https://pypi.python.org/pypi/SQLAlchemy/)
* Flask-SQLAlchemy (https://pypi.python.org/pypi/Flask-SQLAlchemy/)
* Flask-Login (https://pypi.python.org/pypi/Flask-Login/)
* blinker (https://pypi.python.org/pypi/blinker/)
* Flask-Principal (https://pypi.python.org/pypi/Flask-Principal/)
* suds (https://pypi.python.org/pypi/suds/)
* simplejson (https://pypi.python.org/pypi/simplejson/)
* thrift (https://pypi.python.org/pypi/thrift/)
* selenium (https://pypi.python.org/pypi/selenium/)
* patool (https://pypi.python.org/pypi/patool/)
* dbf (https://pypi.python.org/pypi/dbf/)
* alembic (https://pypi.python.org/pypi/alembic/)

Если возникнет ошибка в разрешении зависимостей для одного из модулей, найти необходимый модуль на https://pypi.python.org/pypi/, скачать и установить его.

#### Перенос исходных кодов на сервер

Распаковать архив https://github.com/KorusConsulting/caesar/archive/master.zip в директорию проекта (/srv/my_project)

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

### Автоматическая установка

```
fab alt_deploy
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
