"""add_target_trl_to_ctes

Revision ID: 37dc0fc07d3b
Revises: c50a88fb136a
Create Date: 2026-02-08 12:07:51.098750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37dc0fc07d3b'
down_revision = 'c50a88fb136a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ctes', sa.Column('target_trl', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('ctes', 'target_trl')
