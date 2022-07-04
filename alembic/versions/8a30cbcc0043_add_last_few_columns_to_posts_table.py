"""Add last few columns to posts table

Revision ID: 8a30cbcc0043
Revises: 50b1bec4b990
Create Date: 2022-07-04 09:18:53.952810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a30cbcc0043'
down_revision = '50b1bec4b990'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('published', sa.Boolean(), nullable=False, server_default='True'),)
    op.add_column('posts', sa.Column('created', sa.TIMESTAMP(timezone=True), nullable=False,
                                     server_default=sa.text('NOW()')),)
    pass


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created')
    pass
