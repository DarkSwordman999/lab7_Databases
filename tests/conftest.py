import pytest

import migrate
import school_sqlite as db


@pytest.fixture
def db_path(tmp_path):
    """Путь к новой базе, обновлённой миграциями до последней версии."""
    path = tmp_path / "test.db"
    migrate.upgrade(str(path))
    return str(path)


@pytest.fixture
def connection(db_path):
    conn = db.connect(db_path)
    yield conn
    conn.close()


@pytest.fixture
def filled(connection):
    """База с данными: 3 студента, 2 курса, 3 оценки."""
    ivan = db.insert_student(connection, "Иванов Иван", "221341",
                             "ivan@example.com")
    olga = db.insert_student(connection, "Орлова Ольга", "221341")
    petr = db.insert_student(connection, "Петров Пётр", "221342")
    python = db.insert_course(connection, "Python", 108)
    sql = db.insert_course(connection, "SQL", 72)
    db.insert_grade(connection, ivan, python, 5)
    db.insert_grade(connection, ivan, sql, 4)
    db.insert_grade(connection, olga, python, 3)
    return {"ivan": ivan, "olga": olga, "petr": petr,
            "python": python, "sql": sql}
