# -*- coding: utf-8 -*-
import os
import sys
from sqlalchemy.ext.serializer import loads
from application.app import app, db


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
backups_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alembic', 'backups'))


def restore():
    disable_fk(db.session.bind.engine.url.drivername)
    for bk_file in os.listdir(backups_dir):
        file_path = os.path.join(backups_dir, bk_file)
        if not os.path.isfile(file_path):
            continue
        f = open(file_path, 'rb')
        data = f.read()
        data_list = loads(data)
        model = db.metadata.tables[bk_file]
        db.session.execute(model.insert().values(data_list))
    db.session.commit()
    enable_fk(db.session.bind.engine.url.drivername)
    db.session.remove()


def disable_fk(driver):
    if driver == 'mysql':
        db.session.execute('SET FOREIGN_KEY_CHECKS=0')
    elif driver.find('postgresql') > -1:
        db.session.execute('SET CONSTRAINTS ALL DEFERRED')


def enable_fk(driver):
    if driver == 'mysql':
        db.session.execute('SET FOREIGN_KEY_CHECKS=1')
    elif driver.find('postgresql') > -1:
        pass


if __name__ == '__main__':
    with app.app_context():
        restore()