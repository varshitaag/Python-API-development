"""add foreign key to posts table

Revision ID: 75f164468977
Revises: 8956dc335061
Create Date: 2026-05-01 17:13:59.862624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75f164468977'
down_revision: Union[str, Sequence[str], None] = '8956dc335061'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_users_fk', source_table="posts", referent_table="users", local_cols=["owner_id"], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('post_users_fk',table_name="posts")
    op.drop_column('posts', 'owner_id')
    
    pass
