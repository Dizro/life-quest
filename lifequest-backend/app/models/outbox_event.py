"""
OutboxEvent — паттерн Transactional Outbox.
Таблица ``outbox_events``.

Каждое доменное событие (квест выполнен, уровень повышен, достижение разблокировано)
сначала записывается в эту таблицу внутри той же транзакции, которая изменила агрегат.
Фоновый воркер (Celery beat / polling) забирает строки с ``processed_at IS NULL``
и публикует их в Redis / брокер сообщений, после чего помечает обработанными.

Индексы:
    - ix_outbox_events_processed_at      — быстрый поиск необработанных
    - ix_outbox_events_event_type        — фильтрация по типу события
    - ix_outbox_events_aggregate_id      — корреляция событий по агрегату
    - ix_outbox_events_created_at        — сортировка / очистка по TTL
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    __table_args__ = (
        # составной частичный индекс для polling-запроса:
        #   SELECT * FROM outbox_events
        #   WHERE processed_at IS NULL
        #   ORDER BY created_at ASC  LIMIT 100;
        Index(
            "ix_outbox_unprocessed",
            "processed_at",
            "created_at",
            postgresql_where="processed_at IS NULL",
        ),
    )

    # ── первичный ключ ───────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # ── метаданные события ───────────────────────────────────
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="тип доменного события, например 'quest.completed', 'user.leveled_up'",
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="тип агрегата-источника, например 'user', 'task'",
    )
    aggregate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID агрегата, породившего событие",
    )

    # ── полезная нагрузка ────────────────────────────────────
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="'{}'",
        comment="тело события (JSON)",
    )

    # ── жизненный цикл обработки ─────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="когда событие было записано",
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="когда событие было опубликовано (NULL = ожидает обработки)",
    )

    def __repr__(self) -> str:
        status = "ожидает" if self.processed_at is None else "обработано"
        return f"<OutboxEvent {self.event_type!r} [{status}]>"
