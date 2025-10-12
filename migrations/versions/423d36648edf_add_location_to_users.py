"""add_location_to_users

Revision ID: 423d36648edf
Revises: 003_create_resumes
Create Date: 2025-10-12 15:29:46.915252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '423d36648edf'
down_revision = '003_create_resumes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column('users', sa.Column('location', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column('users', 'location')
