Система администрирования ЛПУ
=================

Для установки ознакомьтесь с системными требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* ОС Windows
* Python 2.7.5 (http://www.python.org/download/)
* СУБД
 * MySQL 5 (http://dev.mysql.com/downloads/installer/)
 * или
 * PostgreSQL ```apt-get install postgresql-server postgresql-client postgresql-contrib``` (руководство по первоначальной установке PostgreSQL можно найти в Интернете)
* MySQL 5 (http://dev.mysql.com/downloads/installer/)
* Web-Server Apache2.2 (http://www.sai.msu.su/apache/dist/httpd/binaries/win32/) + mod_wsgi (http://code.google.com/p/modwsgi/wiki/DownloadTheSoftware)
* git (http://git-scm.com/download/win)
* Установить lxml (http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

Под windows используются только 32-bit версии

```
Команды выполняются в консоли (cmd)
```

Установка
-----------
* Установить СУБД (MySQL или PostgreSQL)

При конфигурировании MySQL, рекомендуется установить в my.cnf:

```
lower_case_table_names=2
```
* Создать новую БД, например с именем: caesar.
* Установить Apache
* Скачать модуль mod_wsgi, скопировать в директорию модулей Apache2.2/modules, подключить модуль в конфиге Apache2.2/conf/httpd.conf:

```
LoadModule wsgi_module modules/mod_wsgi.so
```

* Установить Python и прописать его в системный путь (например, через cmd):

```
set PYTHONPATH=%PYTHONPATH%;D:\Python27;D:\Python27\Scripts
set PATH=%PATH%;%PYTHONPATH%
```

### Установка с использованием pip (Internet)


* Установить setup_tools (https://pypi.python.org/pypi/setuptools/0.6c11#downloads)

* Установить pip

```
easy_install.exe pip
```

* Создать директорию проекта, например D:\projects\caesar и перейти в неё в консоли:

```
cd D:\projects\caesar
```

* Установить virtualenv, создать и активировать виртуальную среду

```
pip install virtualenv
virtualenv venv
venv\Scripts\activate
```

* Установить MySQL-python (для MySQL установки)

```
 easy_install MySQL-python
```

* Установить lxml (http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

* Клонировать репозиторий из git, для этого в директории проекта вызвать из контекстного меню Git Bash и выполнить команду:

```
git clone https://github.com/KorusConsulting/Caesar.git code
```

* Установить зависимости через командную строку:

Для MySQL установки:
```
pip install -r code\requirements\mysql.txt
```
Для PostgreSQL установки:
```
pip install -r code\requirements\pgsql.txt
```

**Замечание: в случае, если во время установки возникает проблема вида:**
```
building '_mysql' extension
error: Unable to find vcvarsall.bat
```
**необходимо убедиться, что в системе установлен компилятор C++, который доступен по пути, прописанном в PATH, подробнее с решением проблемы можно ознакомиться по ссылке: 
http://stackoverflow.com/questions/2019827/error-when-install-python-mysql-module-on-windows**

### Установка пакетов вручную

**Создание и активация виртуального окружения**

* Устанавливаем virtualenv (https://pypi.python.org/pypi/virtualenv/)
    * Распаковываем архив и переходим в директорию модуля
    * Выполняем из консоли ```python setup.py install```
* Создаём и активируем виртуальное окружение

```
virtualenv venv
venv\Scripts\activate
```

Далее Python-пакеты будут устанавливаться в активированное виртуальное окружение.

**Общий принцип установки python-модулей**

* Заливаем во временную директорию архив модуля, скаченный с https://pypi.python.org/
* Распаковываем архив и переходим в директорию модуля
* Выполняем из консоли ```python setup.py install```

**Перечень модулей для установки**

* distribute (https://pypi.python.org/pypi/distribute/)
* setuptools (https://pypi.python.org/pypi/setuptools/)
* lxml (https://pypi.python.org/pypi/lxml/)
* Драйвер для работы с СУБД:
 * mysql-python (https://pypi.python.org/pypi/MySQL-python/) - для MySQL установки
 * или
 * psycopg2 (https://pypi.python.org/pypi/psycopg2/) - для PostgreSQL установки
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


Настройка серверного окружения
-----------

* Конфигурирование виртуальных хостов Apache (Apache2.2/conf/extra/httpd-vhosts.conf), секция Virtual Hosts, добавить следующие конфигурации:


```
Listen %SERVER_HOST%:%SERVER_PORT%
<VirtualHost %SERVER_HOST%:%SERVER_PORT%>
    ServerName %SERVER_HOST%:%SERVER_PORT%
    DocumentRoot "%PROJECT_ROOT%"

    ErrorLog logs/%PROJECT_NAME%-error.log
    CustomLog logs/%PROJECT_NAME%-access.log common
    LogLevel warn

    WSGIScriptAlias / "%PROJECT_CODE_ROOT%/wsgi.py"

    <Directory "%PROJECT_ROOT%/">
        AllowOverride All
        Options None
        Order allow,deny
        Allow from all
    </Directory>
</VirtualHost>

WSGIPythonOptimize 2
```

где:

```
%SERVER_HOST% - хост, по которому будет доступна система (как вариант - IP сервера)
%SERVER_PORT% - порт, по которому будет доступна система (например, 5000)
%PROJECT_ROOT% - директория, где располагаются файлы проекта (в нашем примере, D:/projects/caesar)
%PROJECT_NAME% - название проекта (например, caesar)
%PROJECT_CODE_ROOT% - директория, где располагается код проекта (в нашем примере, D:/projects/caesar/code)
```

* Настройка конфига

Переименовать файл config_local.py_mysql в config_local.py и заменить в нем значения настроек на актуальные, например:

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
Параметры подключения к БД соответствуют параметрам, установленным при создании БД.

SERVER_HOST и SERVER_PORT - должны соответствовать %SERVER_HOST% и %SERVER_PORT%, указанным в конфиге апача

* Заменить файл wsgi.py на прилагаемый wsgi.py_win:
* Перезапустить Apache для того, чтобы конфиг вступил в силу
* Создать таблицы БД, выполнив:

```
alembic upgrade head
```
