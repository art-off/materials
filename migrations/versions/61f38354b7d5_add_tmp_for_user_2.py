"""add tmp for User 2

Revision ID: 61f38354b7d5
Revises: b757e3cc4118
Create Date: 2020-02-10 23:12:12.930432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61f38354b7d5'
down_revision = 'b757e3cc4118'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('tmp', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'tmp')
    # ### end Alembic commands ###
