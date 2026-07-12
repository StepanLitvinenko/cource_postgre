"""add_cities_table

Revision ID: 847d46c1ad46
Revises: 46fd2c011852
Create Date: 2026-07-05 13:44:09.234926

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '847d46c1ad46'
down_revision: Union[str, None] = '46fd2c011852'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())