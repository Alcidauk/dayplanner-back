"""activity add column source

Revision ID: bccd89927320
Revises: 16cbe45cbb18
Create Date: 2026-02-09 18:02:27.930730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bccd89927320'
down_revision: Union[str, Sequence[str], None] = '16cbe45cbb18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('activities', sa.Column('source', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('activities', 'source')
