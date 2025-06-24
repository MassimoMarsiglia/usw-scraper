"""added csfloat sales

Revision ID: 17b51e5c19bf
Revises: d818868059f6
Create Date: 2025-06-13 03:13:07.554501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17b51e5c19bf'
down_revision: Union[str, None] = 'd818868059f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('csfloat_sales') as batch_op:
        batch_op.drop_column('date')
        batch_op.add_column(sa.Column('date', sa.Integer(), nullable=False))

def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('csfloat_sales') as batch_op:
        batch_op.drop_column('date')
        batch_op.add_column(sa.Column('date', sa.DATE(), nullable=False))
