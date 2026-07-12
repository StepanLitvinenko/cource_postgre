"""grant_privileges_and_ownership

Revision ID: ff1d90e49b95
Revises: 550cc25757cb
Create Date: 2026-06-28 13:47:37.482239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff1d90e49b95'
down_revision: Union[str, None] = '511d27a742a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())