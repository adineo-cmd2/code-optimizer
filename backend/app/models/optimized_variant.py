from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OptimizedVariant(Base):
    __tablename__ = "optimized_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("optimization_sessions.id"), index=True
    )
    bottleneck_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("bottleneck_records.id"), nullable=True, index=True
    )
    kind: Mapped[str] = mapped_column(String(20), default="balanced")
    code: Mapped[str] = mapped_column(Text, default="")
    complexity: Mapped[str] = mapped_column(String(20), default="")
    readability: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str] = mapped_column(Text, default="")
