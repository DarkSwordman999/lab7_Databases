# Лабораторная работа №7 — Работа с различными СУБД в Python

[![Python check](https://github.com/DarkSwordman999/lab7_Databases/actions/workflows/python-check.yml/badge.svg)](https://github.com/DarkSwordman999/lab7_Databases/actions/workflows/python-check.yml)

**Фураев Владислав Викторович, группа 221341, вариант 10, лабораторная №7.**

## Цель работы

Научиться работать с базами данных из Python: модуль `sqlite3`, SQLAlchemy ORM, миграции Alembic.

## Задания варианта 10

| Сложность | № | Задание | Реализация |
|---|---|---|---|
| Средняя | 10 | Использовать SQLAlchemy для одной таблицы | `orm_students.py` — модель `Student` |
| Средняя | 2 | Вставить данные в таблицу | `school_sqlite.py` — `insert_student`, `insert_students`, `insert_course`, `insert_grade` |
| Средняя | 8 | Выполнить JOIN | `school_sqlite.py` — `grades_report`, `students_average`, `course_statistics`, `students_without_grade` |
| Повышенная | 10 | Unit-тесты базы данных | `tests/` — 32 теста pytest |
| Повышенная | 3 | Миграции Alembic | `alembic.ini`, `migrations/versions/0001…0004` |

Предметная область — учёт студентов, курсов и оценок.

## Схема базы и миграции (повышенная №3)

Схему создают не `CREATE TABLE` в коде, а миграции Alembic. Каждое изменение структуры — отдельная версия со своими `upgrade()` и `downgrade()`:

| Версия | Что делает |
|---|---|
| `0001` | таблица `students (id, full_name, group_name)` |
| `0002` | новый столбец `students.email` и уникальный индекс `ix_students_email` |
| `0003` | таблицы `courses` и `grades` с внешними ключами (`ON DELETE CASCADE`), проверкой оценки `CHECK (value BETWEEN 2 AND 5)` и ограничением «одна оценка по курсу» `UNIQUE (student_id, course_id)` |
| `0004` | индекс `ix_grades_course_id` для отчётов с JOIN по курсу |

SQLite почти не поддерживает `ALTER TABLE`, поэтому миграции работают в batch-режиме (`op.batch_alter_table`, `render_as_batch=True`): Alembic пересоздаёт таблицу с новой структурой и переносит строки. Тест проверяет, что при откате `0002` данные студентов сохраняются.

Адрес базы берётся из `-x db=...`, затем из переменной `DATABASE_URL`, затем из `alembic.ini`. Из Python миграции запускает `migrate.py` (`migrate.upgrade(path)`), его используют демо и тесты.

```text
$ alembic history
0003 -> 0004 (head), add index on grades.course_id
0002 -> 0003, create courses and grades tables
0001 -> 0002, add email column to students
<base> -> 0001, create students table

$ alembic -x db=sqlite:///demo.db upgrade head

$ alembic -x db=sqlite:///demo.db current
0004 (head)

$ alembic -x db=sqlite:///demo.db downgrade 0002

$ alembic -x db=sqlite:///demo.db current
0002

$ alembic -x db=sqlite:///demo.db upgrade head
```

## Средняя №2. Вставка данных (`sqlite3`)

- все значения передаются параметрами `?`, поэтому имя вида `O'Brien'); DROP TABLE students;--` сохраняется как обычная строка (это проверяет тест);
- `insert_students` вставляет много строк одним `executemany`;
- каждая вставка выполняется в транзакции `with connection:`. Если одна строка пакета нарушает ограничение, откатывается весь пакет;
- `PRAGMA foreign_keys = ON` включается при каждом подключении, иначе SQLite не проверяет внешние ключи.

## Средняя №8. Запросы с JOIN

| Функция | Запрос |
|---|---|
| `grades_report` | `INNER JOIN` трёх таблиц: студент — курс — оценка |
| `students_average` | `LEFT JOIN` + `GROUP BY` + `AVG`: средний балл, студенты без оценок тоже попадают в отчёт |
| `course_statistics` | `LEFT JOIN` + `COUNT/AVG/MIN/MAX` по каждому курсу |
| `students_without_grade` | `LEFT JOIN … WHERE g.id IS NULL`: кто ещё не получил оценку по курсу |

## Средняя №10. SQLAlchemy для одной таблицы

`orm_students.py` описывает таблицу `students` моделью `Student` в стиле SQLAlchemy 2.0 (`DeclarativeBase`, `Mapped`, `mapped_column`). Операции выполняются через `Session` без ручного SQL: добавление, поиск по группе и части ФИО (`select().where()`), изменение группы (ORM сам формирует `UPDATE`), удаление, подсчёт по группам (`func.count` + `group_by`). ORM работает с той же базой, что создали миграции: тест подтверждает, что строки, вставленные через `sqlite3`, видны через ORM.

## Повышенная №10. Unit-тесты базы данных

32 теста pytest. Фикстура `db_path` для каждого теста создаёт новую базу во временной папке (`tmp_path`) и применяет к ней миграции, фикстура `filled` наполняет её данными.

- `test_migrations.py` — одна линейная ветка версий, схема после каждого шага, откат с сохранением данных, полный цикл `base → head`;
- `test_insert.py` — вставка, `executemany`, безопасность кавычек, ограничения `UNIQUE`/`CHECK`/`FOREIGN KEY`, откат пакета, каскадное удаление;
- `test_joins.py` — точные результаты всех JOIN-запросов, в том числе на пустой базе;
- `test_orm.py` — все операции ORM и уникальность email на уровне базы.

## Запуск

```bash
pip install -r requirements.txt
alembic upgrade head        # создать school.db
python main.py              # демо: миграции, вставка, JOIN, ORM
pytest -v
flake8 .
```

GitHub Actions запускает `flake8` и `pytest` при каждом push.

## Пример работы `main.py`

```text
Миграции применены к school.db

Вставлено студентов: 4, курсов: 3, оценок: 6

INNER JOIN: оценки студентов
  full_name                   | group_name | course          | value
  ----------------------------+------------+-----------------+------
  Иванова Мария Сергеевна     | 221341     | Python          | 5
  Иванова Мария Сергеевна     | 221341     | Базы данных     | 4
  Петров Олег Андреевич       | 221342     | Python          | 3
  Фураев Владислав Викторович | 221341     | Python          | 5
  Фураев Владислав Викторович | 221341     | Английский язык | 4
  Фураев Владислав Викторович | 221341     | Базы данных     | 5

LEFT JOIN + GROUP BY: средний балл (включая студентов без оценок)
  full_name                   | grades_count | average
  ----------------------------+--------------+--------
  Фураев Владислав Викторович | 3            | 4.67
  Иванова Мария Сергеевна     | 2            | 4.5
  Петров Олег Андреевич       | 1            | 3.0
  Смирнова Анна Павловна      | 0            | None

Статистика по курсам
  title           | grades_count | average | worst | best
  ----------------+--------------+---------+-------+-----
  Python          | 3            | 4.33    | 3     | 5
  Английский язык | 1            | 4.0     | 4     | 4
  Базы данных     | 2            | 4.5     | 4     | 5

Нет оценки по «Базам данных»: Петров Олег Андреевич, Смирнова Анна Павловна

SQLAlchemy ORM (таблица students)
  добавлен: Student(id=5, 'Кузнецов Илья Романович', 221343)
  группа 221342: ['Кузнецов Илья Романович', 'Петров Олег Андреевич', 'Смирнова Анна Павловна']
  студентов по группам: {'221341': 2, '221342': 3}
```
