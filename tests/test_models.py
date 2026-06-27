"""Structural tests for the CurrencyRates model.

These assert the schema contract that both currency-exchange-rates-api and
currency-exchange-rates-parsers rely on. No database is needed — the DDL is
compiled for the postgres dialect in-memory.
"""

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from currex_schema import CurrencyRates

EXPECTED_COLUMNS = {
    "timestamp",
    "uuid",
    "source",
    "base_currency",
    "target_currency",
    "buy_price",
    "sell_price",
}


def test_table_identity():
    table = CurrencyRates.__table__
    assert table.name == "currency_rates"
    assert table.schema == "public"


def test_columns_and_nullability():
    cols = CurrencyRates.__table__.columns
    assert set(cols.keys()) == EXPECTED_COLUMNS
    # Every column is NOT NULL.
    for col in cols:
        assert col.nullable is False, f"{col.name} should be NOT NULL"


def test_composite_primary_key():
    pk = {c.name for c in CurrencyRates.__table__.primary_key.columns}
    assert pk == {"timestamp", "uuid"}


def test_postgres_ddl_compiles():
    ddl = str(CreateTable(CurrencyRates.__table__).compile(dialect=postgresql.dialect()))
    assert "public.currency_rates" in ddl
    assert "PRIMARY KEY" in ddl
    # timestamptz, not a naive timestamp.
    assert "TIMESTAMP WITH TIME ZONE" in ddl
