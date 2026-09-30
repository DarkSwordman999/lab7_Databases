import sqlite3

import pytest
from alembic.script import ScriptDirectory

import migrate


def tables(path):
    with sqlite3.connect(path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
        return {row[0] for row in rows}


def columns(path, table):
    with sqlite3.connect(path) as conn:
        return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def indexes(path, table):
    with sqlite3.connect(path) as conn:
        return {row[1] for row in conn.execute(f"PRAGMA index_list({table})")}


def current_revision(path):
    with sqlite3.connect(path) as conn:
        return conn.execute("SELECT version_num FROM alembic_version") \
            .fetchone()[0]


def test_single_linear_history():
    script = ScriptDirectory.from_config(migrate.alembic_config("x.db"))
    assert script.get_heads() == ["0004"]
    revisions = [r.revision for r in script.walk_revisions()]
    assert revisions == ["0004", "0003", "0002", "0001"]


def test_upgrade_head_creates_schema(db_path):
    assert tables(db_path) == {"alembic_version", "students", "courses",
                               "grades"}
    assert columns(db_path, "students") == ["id", "full_name",
                                            "group_name", "email"]
    assert "ix_students_email" in indexes(db_path, "students")
    assert "ix_grades_course_id" in indexes(db_path, "grades")
    assert current_revision(db_path) == "0004"


@pytest.mark.parametrize("revision, expected_tables, student_columns", [
    ("0001", {"students"}, ["id", "full_name", "group_name"]),
    ("0002", {"students"}, ["id", "full_name", "group_name", "email"]),
    ("0003", {"students", "courses", "grades"},
     ["id", "full_name", "group_name", "email"]),
])
def test_each_step(tmp_path, revision, expected_tables, student_columns):
    path = str(tmp_path / "step.db")
    migrate.upgrade(path, revision)
    assert tables(path) - {"alembic_version"} == expected_tables
    assert columns(path, "students") == student_columns
    assert current_revision(path) == revision


def test_downgrade_keeps_data(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO students (full_name, group_name, email) "
                     "VALUES ('Тест Тестов', '221341', 't@example.com')")
    migrate.downgrade(db_path, "0001")
    assert tables(db_path) == {"alembic_version", "students"}
    assert columns(db_path, "students") == ["id", "full_name", "group_name"]
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT full_name FROM students").fetchall()
    assert rows == [("Тест Тестов",)]  # batch-режим перенёс строки


def test_full_round_trip(db_path):
    migrate.downgrade(db_path, "base")
    assert tables(db_path) == {"alembic_version"}
    migrate.upgrade(db_path)
    assert current_revision(db_path) == "0004"
