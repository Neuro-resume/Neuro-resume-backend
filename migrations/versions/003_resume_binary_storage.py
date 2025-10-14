"""Store resume as binary content with MIME metadata

Revision ID: 003_resume_binary_storage
Revises: 002_create_sessions
Create Date: 2025-10-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "003_resume_binary_storage"
down_revision: Union[str, None] = "002_create_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to store resume as binary with MIME type."""
    op.add_column(
        "interview_sessions",
        sa.Column("resume_content", sa.LargeBinary(), nullable=True),
    )
    op.add_column(
        "interview_sessions",
        sa.Column("resume_format", sa.String(length=64), nullable=True),
    )

    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE interview_sessions
            SET
                resume_content = CASE
                    WHEN resume_markdown IS NOT NULL
                    THEN convert_to(resume_markdown, 'UTF8')
                    ELSE NULL
                END,
                resume_format = CASE
                    WHEN resume_markdown IS NOT NULL THEN 'text/markdown'
                    ELSE NULL
                END
            """
        )
    )

    op.drop_column("interview_sessions", "resume_markdown")


def downgrade() -> None:
    """Revert schema back to text-based resume storage."""
    op.add_column(
        "interview_sessions",
        sa.Column("resume_markdown", sa.Text(), nullable=True),
    )

    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE interview_sessions
            SET resume_markdown = CASE
                WHEN resume_content IS NOT NULL
                THEN convert_from(resume_content, 'UTF8')
                ELSE NULL
            END
            """
        )
    )

    op.drop_column("interview_sessions", "resume_content")
    op.drop_column("interview_sessions", "resume_format")
