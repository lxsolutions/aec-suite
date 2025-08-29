"""initial schema setup

Revision ID: eee7d2253d24
Revises: 
Create Date: 2025-08-27 05:12:51.236514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eee7d2253d24'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



# Import UUID and JSONB types
from sqlalchemy.dialects.postgresql import UUID, JSONB


def upgrade() -> None:
    """Upgrade schema."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false')
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('data', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )

    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Create agent_runs table
    op.create_table(
        'agent_runs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('input_data', JSONB, nullable=True),
        sa.Column('output_data', JSONB, nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )

    # Create knowledge_base table
    op.create_table(
        'knowledge_base',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('embedding', JSONB, nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('doc_metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_agent_runs_projects',
        source='agent_runs',
        referent='projects',
        local_cols=['project_id'],
        remote_cols=['id']
    )





def downgrade() -> None:
    """Downgrade schema."""

    # Drop foreign key first
    op.drop_constraint('fk_agent_runs_projects', 'agent_runs')

    # Drop tables in reverse order of creation
    op.drop_table('knowledge_base')
    op.drop_table('agent_runs')
    op.drop_table('agents')
    op.drop_table('projects')
    op.drop_table('users')
