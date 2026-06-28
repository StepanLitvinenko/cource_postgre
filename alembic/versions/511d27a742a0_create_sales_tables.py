"""create_sales_tables

Revision ID: 511d27a742a0
Revises: 5fb17b693e9e
Create Date: 2026-06-20 14:29:58.855195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '511d27a742a0'
down_revision: Union[str, None] = '5fb17b693e9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())