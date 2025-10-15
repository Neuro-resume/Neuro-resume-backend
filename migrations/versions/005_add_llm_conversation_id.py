"""Add llm conversation id to interview sessions

Revision ID: 005_add_llm_conversation_id
Revises: 004_drop_language
Create Date: 2025-10-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005_add_llm_conversation_id"
down_revision: Union[str, None] = "004_drop_language"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "interview_sessions",
        sa.Column(
            "llm_conversation_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.execute(
        "UPDATE interview_sessions SET llm_conversation_id = id WHERE llm_conversation_id IS NULL"
    )
    op.alter_column(
        "interview_sessions",
        "llm_conversation_id",
        nullable=False,
    )
    op.create_index(
        "ix_interview_sessions_llm_conversation_id",
        "interview_sessions",
        ["llm_conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_interview_sessions_llm_conversation_id",
        table_name="interview_sessions",
    )
    op.drop_column("interview_sessions", "llm_conversation_id")
