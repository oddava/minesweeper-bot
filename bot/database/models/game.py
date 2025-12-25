from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.models.base import Base, big_int_pk, created_at


class GameRecordModel(Base):
    __tablename__ = "game_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    game_mode: Mapped[str] = mapped_column(String(20), default="beginner")  # beginner, intermediate, expert, custom
    rows: Mapped[int] = mapped_column(default=9)
    cols: Mapped[int] = mapped_column(default=9)
    mines: Mapped[int] = mapped_column(default=10)
    score: Mapped[int]  # Time in seconds
    is_win: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]
