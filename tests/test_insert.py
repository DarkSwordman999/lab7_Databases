import sqlite3

import pytest

import school_sqlite as db


def test_insert_student_returns_id(connection):
    first = db.insert_student(connection, "Иванов Иван", "221341")
    second = db.insert_student(connection, "Петров Пётр", "221341")
    assert (first, second) == (1, 2)
    row = connection.execute("SELECT * FROM students WHERE id = ?",
                             (second,)).fetchone()
    assert dict(row) == {"id": 2, "full_name": "Петров Пётр",
                         "group_name": "221341", "email": None}


def test_insert_many(connection):
    total = db.insert_students(connection, [
        ("А", "1", None), ("Б", "1", None), ("В", "2", "v@example.com")])
    assert total == 3


def test_quotes_are_safe(connection):
    name = "O'Brien'); DROP TABLE students;--"
    student_id = db.insert_student(connection, name, "221341")
    stored = connection.execute("SELECT full_name FROM students WHERE id=?",
                                (student_id,)).fetchone()[0]
    assert stored == name


def test_email_must_be_unique(connection):
    db.insert_student(connection, "А", "1", "same@example.com")
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_student(connection, "Б", "1", "same@example.com")


def test_failed_batch_is_rolled_back(connection):
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_students(connection, [("А", "1", "a@example.com"),
                                        ("Б", "1", "a@example.com")])
    count = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    assert count == 0  # первая строка тоже не сохранилась


@pytest.mark.parametrize("value", [1, 6, 0])
def test_grade_range_check(filled, connection, value):
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_grade(connection, filled["petr"], filled["python"], value)


def test_grade_foreign_key(connection):
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_grade(connection, 999, 999, 5)


def test_one_grade_per_course(filled, connection):
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_grade(connection, filled["ivan"], filled["python"], 4)


def test_course_hours_positive(connection):
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_course(connection, "Пустой курс", 0)


def test_delete_student_cascades_grades(filled, connection):
    with connection:
        connection.execute("DELETE FROM students WHERE id = ?",
                           (filled["ivan"],))
    left = connection.execute("SELECT COUNT(*) FROM grades").fetchone()[0]
    assert left == 1  # остались только оценки Ольги
