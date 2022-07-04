"""Add foreign key to post table

Revision ID: 50b1bec4b990
Revises: 30a54c466f2d
Create Date: 2022-07-04 09:09:19.379005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50b1bec4b990'
down_revision = '30a54c466f2d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts',
                  sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table='posts', referent_table='users', local_cols=['owner_id'],
                          remote_cols=['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    op.drop_constraint('post_users_fk', table_name='posts')
    op.drop_column('posts', 'owner_id')
    pass
