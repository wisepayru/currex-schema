"""alembic environment for public.currency_rates

the history ships inside this package rather than in a consuming repository, because the model does: currex-api
and the two parsers all install this package and resolve the same class from it, so a schema change is a release
of this package and a pin bump in the consumers, which their existing pin guards already watch.

`public` is the database's default schema and holds nothing else this history owns, so the filter is by table
name and not by schema alone
"""
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import URL, create_engine, pool

from currex_schema import Base

SCHEMA = 'public'
TABLES = frozenset({'currency_rates'})

config = context.config
# without this the logging section of alembic.ini is never applied, python's default WARNING root
# filters alembic's own output, and a migration that ran says nothing about which revisions it applied
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def _managed(schema, name) -> bool:
    return (schema or SCHEMA) == SCHEMA and name in TABLES


def include_object(object_, name, type_, reflected, compare_to):
    """every other schema in this database belongs to another history"""
    if type_ == 'table':
        return _managed(object_.schema, name)
    table = getattr(object_, 'table', None)
    if table is not None:
        return _managed(table.schema, table.name)
    return True


def database_url() -> URL:
    # URL.create escapes each component itself. building the dsn by interpolation instead lets a reserved
    # character in the password reshape the url, after which the driver resolves a hostname made of password
    # fragments and prints it in the error
    return URL.create(
        drivername='postgresql',
        username=os.environ.get('POSTGRES_USERNAME'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=int(os.environ['POSTGRES_PORT']) if os.environ.get('POSTGRES_PORT') else None,
        database=os.environ.get('POSTGRES_DATABASE'),
    )


def run_migrations_offline() -> None:
    context.configure(
        url=database_url().render_as_string(hide_password=False),
        target_metadata=target_metadata,
        include_schemas=True,
        include_object=include_object,
        version_table_schema=SCHEMA,
        compare_type=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        # everything this history creates has to belong to wisepay_owner, because that is the role the default
        # privileges in grants.sql are declared for. the migrator is a member of it and owns nothing itself.
        # unconditional on purpose: a switch that could turn this off would, the one time it was set wrongly,
        # leave the new objects owned by the migrator and outside every grant. a database without the role
        # creates it first, which is what the test workflow and local-dev do
        connection.exec_driver_sql('SET ROLE wisepay_owner')
        # committing here is not ceremony: exec_driver_sql opens a transaction, and alembic's own
        # begin_transaction then nests inside it and never commits, so every statement of the migration is
        # rolled back when the connection closes and the run still exits zero. the role is set for the session,
        # so it survives this commit
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            version_table_schema=SCHEMA,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
