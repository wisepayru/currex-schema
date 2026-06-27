from sqlalchemy import (
    Column,
    Float,
    String,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class CurrencyRates(Base):
    __tablename__ = 'currency_rates'
    __table_args__ = {'schema': 'public'}

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        primary_key=True,
    )
    uuid = Column(
        UUID(as_uuid=True),
        nullable=False,
        primary_key=True
    )
    source = Column(
        String,
        nullable=False
    )
    base_currency = Column(
        String,
        nullable=False
    )
    target_currency = Column(
        String,
        nullable=False
    )
    buy_price = Column(
        Float,
        nullable=False
    )
    sell_price = Column(
        Float,
        nullable=False
    )
