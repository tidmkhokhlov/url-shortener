from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base


class ShortUrl(Base):
    __tablename__ = "short_urls"

    slug: Mapped[str] = mapped_column(primary_key=True)
    long_url: Mapped[str]
