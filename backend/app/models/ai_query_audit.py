from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIQueryAudit(Base):
    __tablename__ = "ai_query_audits"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    selected_tool: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    source: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    execution_time_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    error_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        ForeignKeyConstraint(
            ["tenant_id", "user_id"],
            ["users.tenant_id", "users.id"],
        ),
        Index(
            "ix_ai_query_audits_tenant_created",
            "tenant_id",
            "created_at",
        ),
        Index(
            "ix_ai_query_audits_user_created",
            "user_id",
            "created_at",
        ),
        {"mysql_engine": "InnoDB"},
    )