"""add icon theme column

Revision ID: 005
Revises: 004
Create Date: 2024-03-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Add icon_theme column to users table
    op.add_column('users',
        sa.Column('icon_theme', sa.String(), 
                  nullable=True, 
                  server_default='Rainbow Animation')
    )

def downgrade():
    # Remove icon_theme column from users table
    op.drop_column('users', 'icon_theme') 