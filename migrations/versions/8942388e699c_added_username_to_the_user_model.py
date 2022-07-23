"""added username to the User model

Revision ID: 8942388e699c
Revises: 04e5cc0c4e12
Create Date: 2022-07-23 17:53:14.907606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8942388e699c'
down_revision = '04e5cc0c4e12'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(length=20), nullable=False))
    op.create_unique_constraint(None, 'users', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'username')
    # ### end Alembic commands ###