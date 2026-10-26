"""replace users created_at with role

Revision ID: 4c1d8a7e2f90
Revises: 9a4b2c7d1e6f
Create Date: 2026-10-26 11:22:17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4c1d8a7e2f90"
down_revision: Union[str, Sequence[str], None] = "9a4b2c7d1e6f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            server_default=sa.text("'user'"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('user', 'admin')",
    )
    op.drop_column("users", "created_at")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
