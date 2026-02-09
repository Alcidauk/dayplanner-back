"""token add column google tokens

Revision ID: 163c83dfb807
Revises: bccd89927320
Create Date: 2026-02-09 19:39:40.587698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '163c83dfb807'
down_revision: Union[str, Sequence[str], None] = 'bccd89927320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tokens', sa.Column('google_access_token', sa.String(), nullable=True))
    op.add_column('tokens', sa.Column('google_refresh_token', sa.String(), nullable=True))
    op.add_column('tokens', sa.Column('google_token_expiry', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tokens', 'google_access_token')
    op.drop_column('tokens', 'google_refresh_token')
    op.drop_column('tokens', 'google_token_expiry')

