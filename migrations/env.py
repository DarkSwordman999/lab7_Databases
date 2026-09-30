"""Окружение Alembic: откуда брать адрес базы и как выполнять миграции."""

import os

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

# Приоритет адреса БД: -x db=... > DATABASE_URL > alembic.ini
url = (context.get_x_argument(as_dictionary=True).get("db")
       or os.environ.get("DATABASE_URL"))
if url:
    config.set_main_option("sqlalchemy.url", url)

# Миграции пишутся вручную, автогенерация по моделям не используется.
target_metadata = None


def run_migrations_offline():
    """Режим --sql: вывести SQL-скрипт без подключения к базе."""
    context.configure(url=config.get_main_option("sqlalchemy.url"),
                      target_metadata=target_metadata,
                      literal_binds=True,
                      render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        # render_as_batch: SQLite не умеет большинство ALTER TABLE,
        # batch-режим пересоздаёт таблицу с нужной структурой
        context.configure(connection=connection,
                          target_metadata=target_metadata,
                          render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
