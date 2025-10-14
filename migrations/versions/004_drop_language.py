"""Remove language column and normalize progress structure

Revision ID: 004_drop_language
Revises: 003_resume_binary_storage
Create Date: 2025-10-14 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "004_drop_language"
down_revision: Union[str, None] = "003_resume_binary_storage"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop language column/enum and normalize progress payloads."""
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = {col["name"]
               for col in inspector.get_columns("interview_sessions")}

    if "language" in columns:
        with op.batch_alter_table("interview_sessions") as batch_op:
            batch_op.drop_column("language")

    # Remove obsolete enum type if it still exists
    bind.execute(text("DROP TYPE IF EXISTS language"))

    # Ensure progress JSON contains only the percentage field
    bind.execute(
        text(
            """
            UPDATE interview_sessions
            SET progress = jsonb_build_object(
                'percentage',
                COALESCE(
                    NULLIF(progress->>'percentage', '')::int,
                    0
                )
            )
            WHERE progress IS NOT NULL
            """
        )
    )


def downgrade() -> None:
    """Recreate language enum/column and skip progress transformation."""
    bind = op.get_bind()

    # Recreate enum type first
    bind.execute(
        text("CREATE TYPE IF NOT EXISTS language AS ENUM ('ru', 'en')"))

    columns = {col["name"]
               for col in inspect(bind).get_columns("interview_sessions")}
    if "language" not in columns:
        with op.batch_alter_table("interview_sessions") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "language",
                    sa.Enum("ru", "en", name="language", create_type=False),
                    nullable=True,
                )
            )

    # Downgrade does not restore previous progress structure due to ambiguity
