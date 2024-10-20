"""Initial Migration

Revision ID: 051bfdac7e04
Revises: 
Create Date: 2024-10-03 16:01:53.144421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '051bfdac7e04'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('favorite_color', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('favorite_color')

    # ### end Alembic commands ###
