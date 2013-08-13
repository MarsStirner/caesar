# -*- encoding: utf-8 -*-

"""Add xml_encoding to tfoms_config

Revision ID: 10dc65846045
Revises: 43ff41db1d13
Create Date: 2013-08-13 13:53:55.647241

"""

# revision identifiers, used by Alembic.
revision = '10dc65846045'
down_revision = '43ff41db1d13'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

connection = op.get_bind()


def upgrade():
    query = text("""INSERT INTO tfoms_config (id, code, name, value, value_type)
                     VALUES (:id, :code, :name, :value, :value_type)""")
    connection.execute(query,
                       id=4, code='xml_encoding', name=u'Кодировка XML-файлов', value='windows-1251', value_type='enum')


def downgrade():
    query = text("""DELETE FROM tfoms_config WHERE id=:id""")
    connection.execute(query, id=4)
