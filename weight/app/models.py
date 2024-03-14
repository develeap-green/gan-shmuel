import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

# class Example(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     username: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
#     message: so.Mapped[str] = so.mapped_column(sa.String(256))
#     timestamp: so.Mapped[datetime] = so.mapped_column( default=lambda: datetime.now())
#     room: so.Mapped[str] = so.mapped_column(sa.String(32))
