import sys
from pathlib import Path
import unittest

# Ensure project root is in sys.path for direct execution
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.tools.education_tools import get_student, get_student_courses, get_course


class TestEducationTools(unittest.TestCase):

    def test_get_student_existing(self):
        result = get_student("S101")
        self.assertEqual(result.get("student_id"), "S101")
        self.assertEqual(result.get("student_name"), "Alice Vance")

    def test_get_student_not_found(self):
        result = get_student("S999")
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    def test_get_student_courses_existing(self):
        courses = get_student_courses("S101")
        self.assertIsInstance(courses, list)
        self.assertGreaterEqual(len(courses), 1)
        first_course = courses[0]
        self.assertIn("course_name", first_course)
        self.assertIn("marks", first_course)
        self.assertIn("grade", first_course)
        self.assertIn("attendance", first_course)

    def test_get_student_courses_not_found(self):
        result = get_student_courses("S999")
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    def test_get_course_existing(self):
        result = get_course("CS101")
        self.assertEqual(result.get("course_id"), "CS101")
        self.assertEqual(result.get("course_name"), "Introduction to Computer Science")
        self.assertEqual(result.get("teacher_name"), "Dr. Alan Turing")

    def test_get_course_not_found(self):
        result = get_course("UNKNOWN_COURSE")
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())


if __name__ == "__main__":
    unittest.main()
