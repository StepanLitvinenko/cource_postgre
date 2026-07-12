"""create_inventory_schema_and_tables

Revision ID: [7b3bf60da280]
Revises: [предыдущая_ревизия]
Create Date: 2026-07-05 12:00:00.000000

"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7b3bf60da280'
down_revision: Union[str, None] = '847d46c1ad46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql_dir = Path(__file__).parent / "sql" / revision / "up"

    sql_files = sorted(sql_dir.glob("*.sql"))

    for sql_file in sql_files:
        with open(sql_file) as f:
            op.execute(f.read())


def downgrade() -> None:
    sql_dir = Path(__file__).parent / "sql" / revision / "down"
    sql_files = sorted(sql_dir.glob("*.sql"), reverse=True)

    for sql_file in sql_files:
        with open(sql_file) as f:
            op.execute(f.read())