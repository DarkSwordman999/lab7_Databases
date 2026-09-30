"""Лабораторная работа №7, вариант 10 — демонстрация.

1. База создаётся миграциями Alembic.
2. Данные вставляются через sqlite3.
3. Отчёты строятся запросами с JOIN.
4. Таблица students изменяется через SQLAlchemy ORM.
"""

import os
import sys

import migrate
import orm_students as orm
import school_sqlite as db

DB_PATH = "school.db"

STUDENTS = [
    ("Фураев Владислав Викторович", "221341", "furaev@example.com"),
    ("Иванова Мария Сергеевна", "221341", "ivanova@example.com"),
    ("Петров Олег Андреевич", "221342", None),
    ("Смирнова Анна Павловна", "221342", "smirnova@example.com"),
]
COURSES = [("Базы данных", 72), ("Python", 108), ("Английский язык", 36)]
GRADES = [  # (номер студента, номер курса, оценка), нумерация с 1
    (1, 1, 5), (1, 2, 5), (1, 3, 4),
    (2, 1, 4), (2, 2, 5),
    (3, 2, 3),
]


def print_table(rows):
    if not rows:
        print("  (пусто)")
        return
    headers = list(rows[0])
    widths = [max(len(str(h)), *(len(str(r[h])) for r in rows))
              for h in headers]
    line = "  " + " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("  " + "-+-".join("-" * w for w in widths))
    for row in rows:
        print("  " + " | ".join(str(row[h]).ljust(w)
                                for h, w in zip(headers, widths)))


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    migrate.upgrade(DB_PATH)
    print(f"Миграции применены к {DB_PATH}\n")

    connection = db.connect(DB_PATH)
    total = db.insert_students(connection, STUDENTS)
    course_ids = [db.insert_course(connection, *c) for c in COURSES]
    for student, course, value in GRADES:
        db.insert_grade(connection, student, course_ids[course - 1], value)
    print(f"Вставлено студентов: {total}, курсов: {len(course_ids)}, "
          f"оценок: {len(GRADES)}")

    print("\nINNER JOIN: оценки студентов")
    print_table(db.grades_report(connection))
    print("\nLEFT JOIN + GROUP BY: средний балл (включая студентов без "
          "оценок)")
    print_table(db.students_average(connection))
    print("\nСтатистика по курсам")
    print_table(db.course_statistics(connection))
    print("\nНет оценки по «Базам данных»:",
          ", ".join(db.students_without_grade(connection, "Базы данных")))
    connection.close()

    print("\nSQLAlchemy ORM (таблица students)")
    engine = orm.make_engine(DB_PATH)
    with orm.Session(engine) as session:
        new = orm.add_student(session, "Кузнецов Илья Романович", "221343")
        print("  добавлен:", new)
        orm.change_group(session, new.id, "221342")
        print("  группа 221342:",
              [s.full_name for s in orm.find_by_group(session, "221342")])
        print("  студентов по группам:", orm.count_by_group(session))
    engine.dispose()


if __name__ == "__main__":
    sys.exit(main())
