"""Работа с базой через встроенный модуль sqlite3.

Средняя №2 — вставка данных: insert_* функции.
Средняя №8 — JOIN: функции-отчёты внизу модуля.

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


# ---------- средняя №8: запросы с JOIN ----------

def grades_report(connection):
    """INNER JOIN трёх таблиц: кто, по какому курсу, какую оценку получил."""
    return [dict(row) for row in connection.execute("""
        SELECT s.full_name, s.group_name, c.title AS course, g.value
        FROM grades AS g
        JOIN students AS s ON s.id = g.student_id
        JOIN courses  AS c ON c.id = g.course_id
        ORDER BY s.full_name, c.title
    """)]


def students_average(connection):
    """LEFT JOIN + GROUP BY: средний балл каждого студента.

    Студенты без оценок тоже попадают в отчёт (average = None),
    чего не было бы при обычном INNER JOIN.
    """
    return [dict(row) for row in connection.execute("""
        SELECT s.full_name,
               COUNT(g.id)            AS grades_count,
               ROUND(AVG(g.value), 2) AS average
        FROM students AS s
        LEFT JOIN grades AS g ON g.student_id = s.id
        GROUP BY s.id
        ORDER BY average DESC NULLS LAST, s.full_name
    """)]


def course_statistics(connection):
    """JOIN + агрегаты по курсам: число оценок, средняя, минимум, максимум."""
    return [dict(row) for row in connection.execute("""
        SELECT c.title,
               COUNT(g.id)            AS grades_count,
               ROUND(AVG(g.value), 2) AS average,
               MIN(g.value)           AS worst,
               MAX(g.value)           AS best
        FROM courses AS c
        LEFT JOIN grades AS g ON g.course_id = c.id
        GROUP BY c.id
        ORDER BY c.title
    """)]


def students_without_grade(connection, course_title):
    """Кто ещё не получил оценку по курсу: LEFT JOIN ... IS NULL."""
    rows = connection.execute("""
        SELECT s.full_name
        FROM students AS s
        LEFT JOIN grades AS g
               ON g.student_id = s.id
              AND g.course_id = (SELECT id FROM courses WHERE title = ?)
        WHERE g.id IS NULL
        ORDER BY s.full_name
    """, (course_title,))
    return [row["full_name"] for row in rows]
