"""add_created_by_to_orders

Revision ID: 46fd2c011852
Revises: 4a59acb60400
Create Date: 2026-06-28 16:32:44.700564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46fd2c011852'
down_revision: Union[str, None] = '4a59acb60400'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())