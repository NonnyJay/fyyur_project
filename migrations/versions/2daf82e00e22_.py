"""empty message

Revision ID: 2daf82e00e22
Revises: 476d117d49e3
Create Date: 2022-06-05 17:15:21.230112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2daf82e00e22'
down_revision = '476d117d49e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('date_last_modified', sa.DateTime(), nullable=True))
    op.add_column('venue', sa.Column('date_last_modified', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'date_last_modified')
    op.drop_column('artist', 'date_last_modified')
    # ### end Alembic commands ###
