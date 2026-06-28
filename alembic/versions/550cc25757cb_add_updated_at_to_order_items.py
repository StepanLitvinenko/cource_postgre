"""add_updated_at_to_order_items

Revision ID: 550cc25757cb
Revises: 511d27a742a0
Create Date: 2026-06-20 16:18:35.610248

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '550cc25757cb'
down_revision: Union[str, None] = '511d27a742a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())