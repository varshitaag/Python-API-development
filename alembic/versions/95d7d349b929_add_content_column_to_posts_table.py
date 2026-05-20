"""add content column to posts table

Revision ID: 95d7d349b929
Revises: b21842e225dd
Create Date: 2026-05-01 16:35:06.344785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95d7d349b929'
down_revision: Union[str, Sequence[str], None] = 'b21842e225dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts',sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
