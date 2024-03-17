from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from typing import Optional

Base = declarative_base()


class ContainersRegistered(Base):
    __tablename__ = 'containers_registered'

    container_id: Mapped[str] = mapped_column(String(15), primary_key=True)
    weight: Mapped[Optional[int]] = mapped_column(Integer)
    unit: Mapped[Optional[str]] = mapped_column(String(10))

    def __repr__(self):
        return f'<Container {self.container_id}>'


class Transactions(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    datetime: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    direction: Mapped[Optional[str]] = mapped_column(String(10))
    truck: Mapped[Optional[str]] = mapped_column(String(50))
    containers: Mapped[Optional[str]] = mapped_column(String(10000))
    bruto: Mapped[Optional[int]] = mapped_column(Integer)
    truckTara: Mapped[Optional[int]] = mapped_column(Integer)
    neto: Mapped[Optional[int]] = mapped_column(Integer)
    produce: Mapped[Optional[str]] = mapped_column(String(50))
    session_id: Mapped[Optional[int]] = mapped_column(Integer)

    def __repr__(self):
        return f'<Transaction {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "datetime": self.datetime,
            "direction": self.direction,
            "truck": self.truck,
            "containers": self.containers,
            "bruto": self.bruto,
            "truckTara": self.truckTara,
            "neto": self.neto,
            "produce": self.produce,
            "session_id": self.session_id,
        }
