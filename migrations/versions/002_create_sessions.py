"""Create interview_sessions and messages tables

Revision ID: 002_create_sessions
Revises: 001_create_users
Create Date: 2025-10-12 15:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_create_sessions'
down_revision: Union[str, None] = '001_create_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create interview_sessions and messages tables."""

    # Create SessionStatus enum
    session_status_enum = postgresql.ENUM(
        'IN_PROGRESS', 'COMPLETED', 'ABANDONED',
        name='sessionstatus',
        create_type=False
    )
    session_status_enum.create(op.get_bind(), checkfirst=True)

    # Create Language enum
    language_enum = postgresql.ENUM(
        'RU', 'EN',
        name='language',
        create_type=False
    )
    language_enum.create(op.get_bind(), checkfirst=True)

    # Create MessageRole enum
    message_role_enum = postgresql.ENUM(
        'USER', 'AI',
        name='messagerole',
        create_type=False
    )
    message_role_enum.create(op.get_bind(), checkfirst=True)

    # Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', session_status_enum, nullable=False),
        sa.Column('language', language_enum, nullable=False),
        sa.Column('progress', postgresql.JSONB(
            astext_type=sa.Text()), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for interview_sessions
    op.create_index(op.f('ix_interview_sessions_id'),
                    'interview_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_interview_sessions_user_id'),
                    'interview_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_interview_sessions_status'),
                    'interview_sessions', ['status'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', message_role_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(
            astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for messages
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index(op.f('ix_messages_session_id'),
                    'messages', ['session_id'], unique=False)


def downgrade() -> None:
    """Drop interview_sessions and messages tables."""
    op.drop_index(op.f('ix_messages_session_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_index(op.f('ix_interview_sessions_status'),
                  table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_user_id'),
                  table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_id'),
                  table_name='interview_sessions')
    op.drop_table('interview_sessions')

    # Drop enums
    sa.Enum(name='messagerole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='language').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='sessionstatus').drop(op.get_bind(), checkfirst=True)
