"""add daily_gold_earned column

Revision ID: c001add_gold
Revises: 5836f55174df
Create Date: 2026-05-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c001add_gold'
down_revision: Union[str, None] = '5836f55174df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('daily_gold_earned', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    op.drop_column('users', 'daily_gold_earned')
