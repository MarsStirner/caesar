"""Initial migration

Revision ID: 43ff41db1d13
Revises: None
Create Date: 2013-05-30 18:28:00.482217

"""

# revision identifiers, used by Alembic.
revision = '43ff41db1d13'
down_revision = None

from alembic import op
import sqlalchemy as sa
from restore import restore


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tfoms_download_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.Unicode(length=45), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tfoms_tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=80), nullable=False),
    sa.Column('name', sa.Unicode(length=80), nullable=True),
    sa.Column('is_leaf', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('tfoms_template_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=45), nullable=False),
    sa.Column('download_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['download_type_id'], ['tfoms_download_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tfoms_template',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('archive', sa.Boolean(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['tfoms_template_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tfoms_tag_template_type',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('template_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tfoms_tag.id'], ),
    sa.ForeignKeyConstraint(['template_type_id'], ['tfoms_template_type.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'template_type_id')
    )
    op.create_table('tfoms_tags_tree',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['tfoms_tags_tree.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tfoms_tag.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['tfoms_template.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tfoms_standart_tree',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('template_type_id', sa.Integer(), nullable=False),
    sa.Column('is_necessary', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['tfoms_standart_tags_tree.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tfoms_tag.id'], ),
    sa.ForeignKeyConstraint(['template_type_id'], ['tfoms_template_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    restore()
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tfoms_standart_tree')
    op.drop_table('tfoms_tags_tree')
    op.drop_table('tfoms_tag_template_type')
    op.drop_table('tfoms_template')
    op.drop_table('tfoms_template_type')
    op.drop_table('tfoms_tag')
    op.drop_table('tfoms_download_type')
    ### end Alembic commands ###
