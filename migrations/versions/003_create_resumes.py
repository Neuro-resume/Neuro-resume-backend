"""Create resumes table

Revision ID: 003_create_resumes
Revises: 002_create_sessions
Create Date: 2025-10-12 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_create_resumes'
down_revision: Union[str, None] = '002_create_sessions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create resumes table."""

    # Create ResumeTemplate enum
    resume_template_enum = postgresql.ENUM(
        'MODERN', 'CLASSIC', 'MINIMAL', 'CREATIVE',
        name='resumetemplate',
        create_type=False
    )
    resume_template_enum.create(op.get_bind(), checkfirst=True)

    # Create ResumeLanguage enum
    resume_language_enum = postgresql.ENUM(
        'RU', 'EN',
        name='resumelanguage',
        create_type=False
    )
    resume_language_enum.create(op.get_bind(), checkfirst=True)

    # Create resumes table
    op.create_table(
        'resumes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('template', resume_template_enum, nullable=False),
        sa.Column('language', resume_language_enum, nullable=False),
        sa.Column('data', postgresql.JSONB(
            astext_type=sa.Text()), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_resumes_id'), 'resumes', ['id'], unique=False)
    op.create_index(op.f('ix_resumes_user_id'),
                    'resumes', ['user_id'], unique=False)
    op.create_index(op.f('ix_resumes_session_id'),
                    'resumes', ['session_id'], unique=False)


def downgrade() -> None:
    """Drop resumes table."""
    op.drop_index(op.f('ix_resumes_session_id'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_user_id'), table_name='resumes')
    op.drop_index(op.f('ix_resumes_id'), table_name='resumes')
    op.drop_table('resumes')

    # Drop enums
    sa.Enum(name='resumelanguage').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='resumetemplate').drop(op.get_bind(), checkfirst=True)
