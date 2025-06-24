"""merge multiple heads

Revision ID: d68814390912
Revises: b379ace3da61, e636c2bc57a9
Create Date: 2025-06-23 17:25:48.522660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd68814390912'
down_revision: Union[str, None] = ('b379ace3da61', 'e636c2bc57a9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
