from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from baboteek_api.auth.models import User
from baboteek_api.database import Base


class CompilationHistory(Base):
    __tablename__ = "compilation_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), index=True)

    code: Mapped[str] = mapped_column(Text)
    is_success: Mapped[bool] = mapped_column(Boolean)
    stage: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped[User] = relationship()

class CodeExample(Base):
    __tablename__ = "code_examples"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    code: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)