"""Added a app name

Revision ID: 7e79dff05a2d
Revises: 914a9d36c16a
Create Date: 2022-02-14 12:03:05.418353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e79dff05a2d'
down_revision = '914a9d36c16a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('applications', sa.Column('app_name', sa.String(length=200), nullable=False))
    op.create_unique_constraint(None, 'applications', ['app_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'applications', type_='unique')
    op.drop_column('applications', 'app_name')
    # ### end Alembic commands ###
