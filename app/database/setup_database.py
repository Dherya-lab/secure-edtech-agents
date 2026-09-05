import sqlite3
from pathlib import Path


def get_database_path() -> Path:
    """Resolve the path to data/education.db relative to the project root."""
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "education.db"


def setup_database():
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign key enforcement
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Students Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL
        );
        """
    )

    # 2. Courses Table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            teacher_name TEXT NOT NULL
        );
        """
    )

    # 3. Student Courses Table (Enrollment, grades, marks, attendance)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_courses (
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            marks REAL NOT NULL,
            grade TEXT NOT NULL,
            attendance REAL NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE
        );
        """
    )

    # Synthetic / Fictional Data
    students_data = [
        ("S101", "Alice Vance"),
        ("S102", "Bob Smith"),
        ("S103", "Charlie Brown"),
        ("S104", "Diana Prince"),
        ("S105", "Evan Wright"),
        ("STUDENT001", "Aarav"),
        ("STUDENT002", "Diya"),
        ("STUDENT003", "Rahul"),
        ("STUDENT004", "Meera"),
    ]

    courses_data = [
        ("CS101", "Introduction to Computer Science", "Dr. Alan Turing"),
        ("MATH201", "Calculus and Linear Algebra", "Prof. Katherine Johnson"),
        ("SEC301", "Cybersecurity Fundamentals", "Dr. Ada Lovelace"),
        ("MATH101", "Mathematics", "Prof. Katherine Johnson"),
    ]

    student_courses_data = [
        # Alice Vance
        ("S101", "CS101", 92.5, "A", 95.0),
        ("S101", "MATH201", 85.0, "B", 90.0),
        ("S101", "SEC301", 88.0, "B+", 92.0),
        # Bob Smith
        ("S102", "CS101", 74.0, "C", 82.0),
        ("S102", "MATH201", 68.5, "D", 78.0),
        # Charlie Brown
        ("S103", "CS101", 81.0, "B", 88.0),
        ("S103", "SEC301", 79.5, "C+", 85.0),
        # Diana Prince
        ("S104", "MATH201", 95.0, "A", 98.0),
        ("S104", "SEC301", 96.5, "A", 97.0),
        # Evan Wright
        ("S105", "CS101", 62.0, "D", 70.0),
        ("S105", "MATH201", 58.0, "F", 65.0),
        ("S105", "SEC301", 71.0, "C", 75.0),
        # Team Member Synthetic Dataset
        ("STUDENT001", "MATH101", 86.0, "A", 92.0),
        ("STUDENT002", "MATH101", 74.0, "B", 88.0),
        ("STUDENT003", "MATH101", 61.0, "C", 79.0),
        ("STUDENT004", "MATH101", 95.0, "A+", 97.0),
    ]

    # Insert data safely (idempotent: safe to run again without duplicates)
    cursor.executemany(
        """
        INSERT OR REPLACE INTO students (student_id, student_name)
        VALUES (?, ?);
        """,
        students_data,
    )

    cursor.executemany(
        """
        INSERT OR REPLACE INTO courses (course_id, course_name, teacher_name)
        VALUES (?, ?, ?);
        """,
        courses_data,
    )

    cursor.executemany(
        """
        INSERT OR REPLACE INTO student_courses (student_id, course_id, marks, grade, attendance)
        VALUES (?, ?, ?, ?, ?);
        """,
        student_courses_data,
    )

    conn.commit()
    conn.close()

    print(f"Database successfully created and populated at: {db_path}")


if __name__ == "__main__":
    setup_database()
