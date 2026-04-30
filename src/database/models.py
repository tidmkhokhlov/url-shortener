from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class ShortUrl(Base):
    __tablename__ = "short_urls"

    slug: Mapped[str] = mapped_column(String(6), primary_key=True)
    long_url: Mapped[str] = mapped_column(String(512), nullable=False)
    redirects_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
