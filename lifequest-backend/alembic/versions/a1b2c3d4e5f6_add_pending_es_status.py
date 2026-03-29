"""Add pending_es to task_status enum + missing columns (effort_score, task_type)

Revision ID: a1b2c3d4e5f6
Revises: 27e9be44676d
Create Date: 2026-03-29 12:46:00.000000

Добавляет:
  1. Значение 'pending_es' в enum task_status (BPMN: ожидание ИИ-оценки)
  2. Столбец effort_score (INTEGER, nullable) — оценка сложности от ИИ (0–10)
  3. Столбец task_type (ENUM, NOT NULL, default='regular') — тип задачи
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '27e9be44676d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавить 'pending_es' в enum task_status
    op.execute("ALTER TYPE task_status ADD VALUE IF NOT EXISTS 'pending_es' BEFORE 'active'")

    # 2. Создать enum task_type (если не существует)
    task_type_enum = sa.Enum('regular', 'daily', 'habit', name='task_type', create_constraint=True)
    task_type_enum.create(op.get_bind(), checkfirst=True)

    # 3. Добавить столбец effort_score
    op.add_column('tasks', sa.Column(
        'effort_score',
        sa.Integer(),
        nullable=True,
        comment='оценка сложности от ИИ (0–10)',
    ))

    # 4. Добавить столбец task_type
    op.add_column('tasks', sa.Column(
        'task_type',
        task_type_enum,
        server_default='regular',
        nullable=False,
        comment='тип задачи: regular/daily/habit',
    ))


def downgrade() -> None:
    op.drop_column('tasks', 'task_type')
    op.drop_column('tasks', 'effort_score')
    sa.Enum(name='task_type').drop(op.get_bind(), checkfirst=True)
    # PostgreSQL не позволяет удалить значение из enum без пересоздания
