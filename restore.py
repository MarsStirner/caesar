# -*- coding: utf-8 -*-
import os
import sys
from sqlalchemy.ext.serializer import loads
from application.app import app, db


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
backups_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alembic', 'backups'))

# TODO: разобраться, почему без этой строки не работает
db.app = app


def restore():
    for bk_file in os.listdir(backups_dir):
        f = open(os.path.join(backups_dir, bk_file), 'rb')
        data = f.read()
        data_list = loads(data)
        model = db.metadata.tables[bk_file]
        db.session.execute(model.insert().values(data_list))
        db.session.commit()
    db.session.remove()

if __name__ == '__main__':
    restore()