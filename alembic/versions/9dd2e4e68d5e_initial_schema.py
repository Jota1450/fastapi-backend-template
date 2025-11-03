"""initial_schema

Revision ID: 9dd2e4e68d5e
Revises: 
Create Date: 2025-11-03 02:07:34.901557

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '9dd2e4e68d5e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Ensure uuid-ossp extension is available
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users schema
    op.execute('CREATE SCHEMA IF NOT EXISTS users')
    
    # Create user table in users schema
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=True),  # Nullable for OAuth users
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),  # OAuth avatar URL
        sa.Column('oauth_provider_data', sa.Text(), nullable=True),  # JSON data from OAuth provider
        sa.PrimaryKeyConstraint('id'),
        schema='users'
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True, schema='users')
    
    # Create role table in users schema
    op.create_table(
        'role',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='users'
    )
    op.create_index('ix_role_name', 'role', ['name'], unique=True, schema='users')
    
    # Create user_role table for many-to-many relationship
    op.create_table(
        'user_role',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['users.role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
        schema='users'
    )


def downgrade():
    # Drop user_role table
    op.drop_table('user_role', schema='users')
    
    # Drop role table
    op.drop_index('ix_role_name', table_name='role', schema='users')
    op.drop_table('role', schema='users')
    
    # Drop user table
    op.drop_index('ix_user_email', table_name='user', schema='users')
    op.drop_table('user', schema='users')
    
    # Drop users schema
    op.execute('DROP SCHEMA IF EXISTS users CASCADE')
