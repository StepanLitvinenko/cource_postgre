"""create_auth_schema_and_users_table

Revision ID: 4a59acb60400
Revises: ff1d90e49b95
Create Date: 2026-06-28 14:38:50.921427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a59acb60400'
down_revision: Union[str, None] = 'ff1d90e49b95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/up.sql") as file:
        op.execute(file.read())


def downgrade() -> None:
    with open(f"alembic/versions/sql/{revision}/down.sql") as file:
        op.execute(file.read())