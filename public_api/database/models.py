from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Model(DeclarativeBase):
    pass


class Memes(Model):
    __tablename__ = "memes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meme_name: Mapped[str] = mapped_column(index=True, unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    image_url: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    date_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                                   nullable=False)

    def __repr__(self):
        return (
            f"<Memes(id={self.id}, meme_name='{self.meme_name}', filename='{self.filename}', "
            f"image_url='{self.image_url}', text='{self.text}...', date_added='{self.date_added}', "
            f"date_updated='{self.date_updated}')>"
        )
