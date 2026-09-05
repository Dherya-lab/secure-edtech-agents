import contextlib
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Union


@contextlib.contextmanager
def get_db_connection():
    """Resolve database path and yield a SQLite connection with Row factory enabled, closing it on exit."""
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / "data" / "education.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_student(student_id: str) -> Dict[str, Any]:
    """Return basic information about a student.

    If the student does not exist, return a clear 'student not found' result.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT student_id, student_name FROM students WHERE student_id = ?",
            (student_id,),
        )
        row = cursor.fetchone()
        if not row:
            return {"error": f"Student with ID '{student_id}' not found."}
        return {
            "student_id": row["student_id"],
            "student_name": row["student_name"],
        }


def get_student_courses(
    student_id: str,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """Return the student's courses with course name, marks, grade, and attendance.

    If the student does not exist, return a clear 'student not found' result.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Verify student exists
        cursor.execute(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_id,),
        )
        if not cursor.fetchone():
            return {"error": f"Student with ID '{student_id}' not found."}

        cursor.execute(
            """
            SELECT c.course_id, c.course_name, sc.marks, sc.grade, sc.attendance
            FROM student_courses sc
            JOIN courses c ON sc.course_id = c.course_id
            WHERE sc.student_id = ?
            """,
            (student_id,),
        )
        rows = cursor.fetchall()
        return [
            {
                "course_id": row["course_id"],
                "course_name": row["course_name"],
                "marks": row["marks"],
                "grade": row["grade"],
                "attendance": row["attendance"],
            }
            for row in rows
        ]


def get_course(course_id: str) -> Dict[str, Any]:
    """Return course information including course name and teacher name.

    If the course does not exist, return a clear 'course not found' result.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT course_id, course_name, teacher_name FROM courses WHERE course_id = ?",
            (course_id,),
        )
        row = cursor.fetchone()
        if not row:
            return {"error": f"Course with ID '{course_id}' not found."}
        return {
            "course_id": row["course_id"],
            "course_name": row["course_name"],
            "teacher_name": row["teacher_name"],
        }


if __name__ == "__main__":
    print("--- Demonstrating Education Tools ---")
    print("\n1. get_student('S101'):")
    print(get_student("S101"))

    print("\n2. get_student('S999') [non-existent]:")
    print(get_student("S999"))

    print("\n3. get_student_courses('S101'):")
    print(get_student_courses("S101"))

    print("\n4. get_student_courses('S999') [non-existent]:")
    print(get_student_courses("S999"))

    print("\n5. get_course('CS101'):")
    print(get_course("CS101"))

    print("\n6. get_course('NON_EXISTENT') [non-existent]:")
    print(get_course("NON_EXISTENT"))
