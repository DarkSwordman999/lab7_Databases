import school_sqlite as db


def test_grades_report_inner_join(filled, connection):
    assert db.grades_report(connection) == [
        {"full_name": "Иванов Иван", "group_name": "221341",
         "course": "Python", "value": 5},
        {"full_name": "Иванов Иван", "group_name": "221341",
         "course": "SQL", "value": 4},
        {"full_name": "Орлова Ольга", "group_name": "221341",
         "course": "Python", "value": 3},
    ]


def test_average_includes_students_without_grades(filled, connection):
    report = db.students_average(connection)
    assert report == [
        {"full_name": "Иванов Иван", "grades_count": 2, "average": 4.5},
        {"full_name": "Орлова Ольга", "grades_count": 1, "average": 3.0},
        {"full_name": "Петров Пётр", "grades_count": 0, "average": None},
    ]


def test_course_statistics(filled, connection):
    assert db.course_statistics(connection) == [
        {"title": "Python", "grades_count": 2, "average": 4.0,
         "worst": 3, "best": 5},
        {"title": "SQL", "grades_count": 1, "average": 4.0,
         "worst": 4, "best": 4},
    ]


def test_students_without_grade(filled, connection):
    assert db.students_without_grade(connection, "SQL") == [
        "Орлова Ольга", "Петров Пётр"]
    assert db.students_without_grade(connection, "Python") == [
        "Петров Пётр"]


def test_empty_database(connection):
    assert db.grades_report(connection) == []
    assert db.students_average(connection) == []
