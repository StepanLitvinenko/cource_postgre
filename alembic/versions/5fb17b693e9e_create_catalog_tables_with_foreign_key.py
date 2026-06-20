"""create_catalog_tables_with_foreign_key

Revision ID: 5fb17b693e9e
Revises: 
Create Date: 2026-06-20 14:12:12.243549

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fb17b693e9e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())