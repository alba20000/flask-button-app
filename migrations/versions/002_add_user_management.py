"""Add user management fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and is_active fields to users table
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    # Set created_at for existing users
    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")


def downgrade() -> None:
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'created_at')
