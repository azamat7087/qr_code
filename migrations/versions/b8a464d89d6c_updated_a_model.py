"""Updated a model

Revision ID: b8a464d89d6c
Revises: 93cb79b1d372
Create Date: 2022-02-04 10:32:47.512705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8a464d89d6c'
down_revision = '93cb79b1d372'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('qr_codes', sa.Column('qr_code', sa.String(length=300), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('qr_codes', 'qr_code')
    # ### end Alembic commands ###
