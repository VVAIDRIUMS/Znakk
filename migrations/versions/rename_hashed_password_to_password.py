"""Rename hashed_password to password

Revision ID: abc123def456
Revises: 
Create Date: 2025-12-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename column from hashed_password to password
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              new_column_name='password',
                              existing_type=sa.String(length=300),
                              nullable=False)


def downgrade() -> None:
    # Rename column back from password to hashed_password
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password',
                              new_column_name='hashed_password',
                              existing_type=sa.String(length=300),
                              nullable=False)
