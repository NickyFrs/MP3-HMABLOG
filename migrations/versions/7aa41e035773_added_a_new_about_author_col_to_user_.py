"""added a new about author col to User Model

Revision ID: 7aa41e035773
Revises: 
Create Date: 2022-07-24 19:12:03.684740

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7aa41e035773'
down_revision = None
branch_labels = None
depends_on = None

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


def upgrade():
    with op.batch_alter_table('test', schema=None, naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('fk_test_user_id_user', type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('fk_test_user_id_user'), 'user', ['user_id'], ['id'], ondelete='CASCADE')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'users', ['blogger_id'], ['id'])
        batch_op.drop_column('poster_id')
        batch_op.drop_column('author')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_author', sa.Text(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('about_author')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('poster_id', sa.INTEGER(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###


