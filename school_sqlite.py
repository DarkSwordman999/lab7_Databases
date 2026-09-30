"""Работа с базой через встроенный модуль sqlite3.

Средняя №2 — вставка данных: insert_* функции.

Схему таблиц создают миграции Alembic (папка migrations/).
Все значения передаются параметрами (?), а не подстановкой в строку.
"""

import sqlite3


def connect(db_path):
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    # в SQLite проверка внешних ключей включается для каждого соединения
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ---------- средняя №2: вставка данных ----------

def insert_student(connection, full_name, group_name, email=None):
    with connection:  # транзакция: commit при успехе, rollback при ошибке
        cursor = connection.execute(
            "INSERT INTO students (full_name, group_name, email) "
            "VALUES (?, ?, ?)", (full_name, group_name, email))
    return cursor.lastrowid


def insert_students(connection, students):
    """Вставить много студентов одним вызовом executemany.

    students — последовательность кортежей (ФИО, группа, email).
    """
    with connection:
        connection.executemany(
            "INSERT INTO students (full_name, group_name, email) "
            "VALUES (?, ?, ?)", students)
    return connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]


def insert_course(connection, title, hours):
    with connection:
        cursor = connection.execute(
            "INSERT INTO courses (title, hours) VALUES (?, ?)",
            (title, hours))
    return cursor.lastrowid


def insert_grade(connection, student_id, course_id, value):
    with connection:
        cursor = connection.execute(
            "INSERT INTO grades (student_id, course_id, value) "
            "VALUES (?, ?, ?)", (student_id, course_id, value))
    return cursor.lastrowid
