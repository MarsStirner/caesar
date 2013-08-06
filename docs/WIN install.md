Система администрирования ЛПУ
=================

Для установки ИС ознакомьтесь с системными требованиями и инструкцией, указанными ниже.

Системные требования
-----------

* ОС Windows
* Python 2.7 (http://www.python.org/download/)
* MySQL 5 (http://dev.mysql.com/downloads/installer/)
* Web-Server Apache2.2 (http://www.sai.msu.su/apache/dist/httpd/binaries/win32/) + mod_wsgi (http://code.google.com/p/modwsgi/wiki/DownloadTheSoftware)
* git (http://git-scm.com/download/win)
* Twisted (http://twistedmatrix.com/Releases/Twisted/12.3/Twisted-12.3.0.win32-py2.7.msi)

Под windows используются только 32-bit версии

Установка
-----------
* Установить MySQL

При конфигурировании MySQL, рекомендуется установить в my.cnf:

```
lower_case_table_names=2
```
* Создать новую БД, например с именем: soap.
* Установить Apache
* Скачать модуль mod_wsgi, скопиррвать в директорию модулей Apache2.2/modules, подключить модуль в конфиге Apache2.2/conf/httpd.conf:

```
LoadModule mod_wsgi modules/mod_wsgi.so
```

* Установить Python и прописать его в системный путь (например, через cmd):

```
set PYTHONPATH=%PYTHONPATH%;D:\Python27;D:\Python27\Scripts
set PATH=%PATH%;%PYTHONPATH%
```
* Установить Twisted (http://twistedmatrix.com/Releases/Twisted/12.3/Twisted-12.3.0.win32-py2.7.msi)

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

* Установить MySQL-python

```
 easy_install MySQL-python
```

* Установить lxml (http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

* Клонировать репозиторий из git, для этого в директории проекта вызвать из контекстного меню Git Bash и выполнить команду:

```
git clone https://github.com/KorusConsulting/sobiralka.git code
```

* Установить зависимости через командную строку:

```
pip install -r code\requirements.txt
```

Настройка серверного окружения
-----------

* Конфигурирование виртуальных хостов Apache (Apache2.2/conf/extra/httpd-vhosts.conf), секция Virtual Hosts, добавить следующие конфигурации:

Конфигурирация для ИС:

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

#Хост и порт, по которым будет доступен ИС
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9910
```
Параметры подключения к БД соответствуют параметрам, установленным при создании БД для ИС.

SERVER_HOST и SERVER_PORT - должны соответствовать %SERVER_HOST% и %SERVER_PORT%, указанным в конфиге апача

* Заменить файл wsgi.py на прилагаемый wsgi.py_win:
* Перезапустить Apache для того, чтобы конфиг вступил в силу
* Создать таблицы БД, выполнив:

```
alembic upgrade head
```