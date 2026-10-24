from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BottleneckRecord(Base):
    __tablename__ = "bottleneck_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("optimization_sessions.id"), index=True
    )
    function: Mapped[str] = mapped_column(String(255), default="")
    root_cause: Mapped[str] = mapped_column(String(255), default="")
    predicted_ms: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[str] = mapped_column(String(20), default="low")
    snippet: Mapped[str] = mapped_column(Text, default="")
