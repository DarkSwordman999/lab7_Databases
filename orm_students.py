"""Средняя №10. SQLAlchemy ORM для одной таблицы (students).

Модель Student описывает ту же таблицу, которую создают миграции.
Работа идёт через объекты и сессию, без ручного SQL.
"""

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    group_name: Mapped[str] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(120), unique=True)

    def __repr__(self):
        return f"Student(id={self.id}, {self.full_name!r}, {self.group_name})"


def make_engine(db_path):
    return create_engine(f"sqlite:///{db_path}")


def add_student(session, full_name, group_name, email=None):
    student = Student(full_name=full_name, group_name=group_name,
                      email=email)
    session.add(student)
    session.commit()  # после commit у объекта появляется id
    return student


def find_by_group(session, group_name):
    query = (select(Student).where(Student.group_name == group_name)
             .order_by(Student.full_name))
    return list(session.scalars(query))


def find_by_name_part(session, text):
    query = select(Student).where(Student.full_name.contains(text))
    return list(session.scalars(query))


def change_group(session, student_id, new_group):
    student = session.get(Student, student_id)
    if student is None:
        return None
    student.group_name = new_group  # ORM сам сформирует UPDATE
    session.commit()
    return student


def delete_student(session, student_id):
    student = session.get(Student, student_id)
    if student is None:
        return False
    session.delete(student)
    session.commit()
    return True


def count_by_group(session):
    query = (select(Student.group_name, func.count(Student.id))
             .group_by(Student.group_name).order_by(Student.group_name))
    return dict(session.execute(query).all())


__all__ = ["Base", "Session", "Student", "add_student", "change_group",
           "count_by_group", "delete_student", "find_by_group",
           "find_by_name_part", "make_engine"]
