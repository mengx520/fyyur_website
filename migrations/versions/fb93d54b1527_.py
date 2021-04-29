"""empty message

Revision ID: fb93d54b1527
Revises: 151fdb28907c
Create Date: 2021-04-29 10:57:13.633967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb93d54b1527'
down_revision = '151fdb28907c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'website_link')
    # ### end Alembic commands ###
