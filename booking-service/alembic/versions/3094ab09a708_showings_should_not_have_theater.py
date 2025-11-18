"""showings should not have theater

Revision ID: 3094ab09a708
Revises: 6c32322aa8cb
Create Date: 2025-11-18 23:44:33.975705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3094ab09a708'
down_revision: Union[str, None] = '6c32322aa8cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
