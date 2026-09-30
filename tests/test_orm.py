import pytest
from sqlalchemy.exc import IntegrityError

import orm_students as orm


@pytest.fixture
def session(db_path):
    engine = orm.make_engine(db_path)
    with orm.Session(engine) as s:
        yield s
    engine.dispose()


def test_add_and_get(session):
    student = orm.add_student(session, "Иванов Иван", "221341",
                              "ivan@example.com")
    assert student.id == 1
    assert session.get(orm.Student, 1).email == "ivan@example.com"


def test_find_by_group_sorted(session):
    orm.add_student(session, "Яковлев Ян", "221341")
    orm.add_student(session, "Антонов Антон", "221341")
    orm.add_student(session, "Борисов Борис", "221342")
    names = [s.full_name for s in orm.find_by_group(session, "221341")]
    assert names == ["Антонов Антон", "Яковлев Ян"]


def test_find_by_name_part(session):
    orm.add_student(session, "Иванов Иван", "1")
    orm.add_student(session, "Петров Пётр", "1")
    assert [s.full_name for s in orm.find_by_name_part(session, "ров")] == [
        "Петров Пётр"]


def test_change_group(session):
    student = orm.add_student(session, "Иванов Иван", "221341")
    orm.change_group(session, student.id, "221342")
    session.expire_all()  # перечитать из базы, а не из кэша сессии
    assert session.get(orm.Student, student.id).group_name == "221342"
    assert orm.change_group(session, 999, "x") is None


def test_delete(session):
    student = orm.add_student(session, "Иванов Иван", "221341")
    assert orm.delete_student(session, student.id) is True
    assert session.get(orm.Student, student.id) is None
    assert orm.delete_student(session, student.id) is False


def test_count_by_group(session):
    for name, group in [("А", "1"), ("Б", "1"), ("В", "2")]:
        orm.add_student(session, name, group)
    assert orm.count_by_group(session) == {"1": 2, "2": 1}


def test_unique_email_from_migration(session):
    orm.add_student(session, "А", "1", "same@example.com")
    with pytest.raises(IntegrityError):
        orm.add_student(session, "Б", "1", "same@example.com")
    session.rollback()


def test_orm_sees_rows_inserted_by_sqlite3(filled, session):
    names = sorted(s.full_name for s in session.query(orm.Student))
    assert names == ["Иванов Иван", "Орлова Ольга", "Петров Пётр"]
