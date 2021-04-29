"""empty message

Revision ID: 151fdb28907c
Revises: 5c566f1a2b60
Create Date: 2021-04-28 16:02:56.038179

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '151fdb28907c'
down_revision = '5c566f1a2b60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('genres', sa.String(length=500), nullable=False))
    op.add_column('venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'website_link')
    op.drop_column('venue', 'genres')
    # ### end Alembic commands ###