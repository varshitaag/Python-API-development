"""add verification columns to users table

Revision ID: add_verification_columns
Revises: 75f164468977
Create Date: 2026-05-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_verification_columns'
down_revision: Union[str, Sequence[str], None] = '75f164468977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add verification columns to users table."""
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), server_default='FALSE', nullable=False))
    op.add_column('users', sa.Column('verification_token', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - remove verification columns from users table."""
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_verified')
