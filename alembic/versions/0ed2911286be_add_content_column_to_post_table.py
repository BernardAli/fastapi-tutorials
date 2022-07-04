"""Add content column to post table

Revision ID: 0ed2911286be
Revises: 9d67d0284225
Create Date: 2022-07-02 12:10:18.375984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ed2911286be'
down_revision = '9d67d0284225'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
