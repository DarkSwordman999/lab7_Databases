"""Запуск миграций Alembic из Python (используется демо и тестами).

Из командной строки то же самое делается так:
    alembic upgrade head
    alembic downgrade 0001
"""

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

PROJECT_DIR = Path(__file__).resolve().parent


def alembic_config(db_path):
    config = Config(str(PROJECT_DIR / "alembic.ini"))
    config.set_main_option("script_location",
                           str(PROJECT_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return config


def upgrade(db_path, revision="head"):
    command.upgrade(alembic_config(db_path), revision)


def downgrade(db_path, revision):
    command.downgrade(alembic_config(db_path), revision)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "school.db"
    upgrade(target)
    print(f"База {target} обновлена до последней миграции")
