"""Create table

Revision ID: dc017769bcdd
Revises:
Create Date: 2025-06-04 18:57:29.093078

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dc017769bcdd"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "file_metadata",
        sa.Column("file_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("file_type", sa.String(50)),
        sa.Column("destination", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("tags", sa.String, nullable=True),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("is_deleted", sa.Boolean, nullable=False, default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("file_metadata")
