"""add_org_user_estimate_models

Revision ID: 69f7ac79f32d
Revises: 
Create Date: 2025-08-30 00:13:02.208872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69f7ac79f32d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=False)
    
    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'PM', 'FIELD', name='userrole'), nullable=False, server_default='FIELD'))
    op.add_column('users', sa.Column('org_id', sa.UUID(), nullable=False))
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_users_org_id', 'users', 'organizations', ['org_id'], ['id'])
    
    # Add org_id to projects table
    op.add_column('projects', sa.Column('org_id', sa.UUID(), nullable=False))
    op.create_foreign_key('fk_projects_org_id', 'projects', 'organizations', ['org_id'], ['id'])
    
    # Create estimates table
    op.create_table(
        'estimates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('org_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('material_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('labor_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('equipment_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('subcontractor_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('overhead_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('profit_margin', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('total_cost', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('approved_by', sa.UUID(), nullable=True),
        sa.Column('rejected_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_estimates_project_id'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], name='fk_estimates_org_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_estimates_created_by'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], name='fk_estimates_approved_by'),
        sa.ForeignKeyConstraint(['rejected_by'], ['users.id'], name='fk_estimates_rejected_by')
    )
    
    # Add org_id to agent_runs table
    op.add_column('agent_runs', sa.Column('org_id', sa.UUID(), nullable=False))
    op.create_foreign_key('fk_agent_runs_org_id', 'agent_runs', 'organizations', ['org_id'], ['id'])
    
    # Add org_id to knowledge_base table
    op.add_column('knowledge_base', sa.Column('org_id', sa.UUID(), nullable=False))
    op.create_foreign_key('fk_knowledge_base_org_id', 'knowledge_base', 'organizations', ['org_id'], ['id'])
    
    # Add org_id to agents table
    op.add_column('agents', sa.Column('org_id', sa.UUID(), nullable=False))
    op.create_foreign_key('fk_agents_org_id', 'agents', 'organizations', ['org_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_agents_org_id', 'agents', type_='foreignkey')
    op.drop_column('agents', 'org_id')
    
    op.drop_constraint('fk_knowledge_base_org_id', 'knowledge_base', type_='foreignkey')
    op.drop_column('knowledge_base', 'org_id')
    
    op.drop_constraint('fk_agent_runs_org_id', 'agent_runs', type_='foreignkey')
    op.drop_column('agent_runs', 'org_id')
    
    op.drop_table('estimates')
    
    op.drop_constraint('fk_projects_org_id', 'projects', type_='foreignkey')
    op.drop_column('projects', 'org_id')
    
    op.drop_constraint('fk_users_org_id', 'users', type_='foreignkey')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'org_id')
    op.drop_column('users', 'role')
    
    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_table('organizations')
    
    # Drop the enum type
    op.execute('DROP TYPE userrole')
