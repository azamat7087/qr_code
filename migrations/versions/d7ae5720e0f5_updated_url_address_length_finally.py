"""Updated url address length FINALLY

Revision ID: d7ae5720e0f5
Revises: e2122473980f
Create Date: 2022-02-05 10:46:53.081639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7ae5720e0f5'
down_revision = 'e2122473980f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('qr_codes', 'source_ip',
               existing_type=sa.VARCHAR(length=16),
               type_=sa.String(length=40),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('qr_codes', 'source_ip',
               existing_type=sa.String(length=40),
               type_=sa.VARCHAR(length=16),
               existing_nullable=False)
    # ### end Alembic commands ###
