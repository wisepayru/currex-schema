# currex-schema

Shared SQLAlchemy models for the wisepay currency-exchange rates database.

The `public.currency_rates` table is **written by**
[`currency-exchange-rates-parsers`](https://github.com/wisepayru/currency-exchange-rates-parsers)
and **read by**
[`currency-exchange-rates-api`](https://github.com/wisepayru/currency-exchange-rates-api).
Both consume this package so the two never drift on the schema.

## Use

Pin to a release tag (per the #108 dependency discipline), like the other
wisepay packages:

```
currex-schema @ git+https://github.com/wisepayru/currex-schema.git@<tag>
```

```python
from currex_schema import Base, CurrencyRates
# or: from currex_schema.models import Base, CurrencyRates
```

## Migrations

This package holds **only the ORM models** — there is no migration tooling. A
schema change is a coordinated, manual operation:

1. Change the model here and cut a new release tag.
2. Bump the pin in **both** consumers.
3. Apply the `ALTER TABLE` once, by hand, on the shared DB (QA then prod). The
   consumers' deploy workflows guard on the model-pin change so the manual
   migration isn't forgotten.

## Develop

```sh
python3.14 -m venv .venv
.venv/bin/pip install -e . -r requirements-test.txt
.venv/bin/ruff check .
.venv/bin/pytest
```

No database is required — the tests compile the DDL in-memory for the postgres
dialect.

## Releasing

The version is derived from the git tag by `setuptools-scm`. Publish a GitHub
Release with the new tag; `release-artifacts.yml` builds a wheel + sdist and
attaches them to the release (the primary consumption path stays
`pip install git+...@<tag>`).
