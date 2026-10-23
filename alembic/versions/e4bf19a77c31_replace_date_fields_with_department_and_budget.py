"""replace date fields with department and budget

Revision ID: e4bf19a77c31
Revises: d0778f02d3fd
Create Date: 2026-10-23 14:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4bf19a77c31"
down_revision: Union[str, Sequence[str], None] = "d0778f02d3fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("Employee", "joining_date")
    op.add_column(
        "Employee",
        sa.Column("department", sa.String(length=100), nullable=True),
    )
    op.drop_column("Projects", "start_date")
    op.add_column(
        "Projects",
        sa.Column("budget", sa.Numeric(precision=12, scale=2), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("Employee", "department")
    op.add_column("Employee", sa.Column("joining_date", sa.Date(), nullable=True))
    op.drop_column("Projects", "budget")
    op.add_column("Projects", sa.Column("start_date", sa.Date(), nullable=True))
