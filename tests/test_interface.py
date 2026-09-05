from pathlib import Path
import sys
import unittest
from unittest.mock import patch

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.interface.api import app
from teacher_agent_interface import run_teacher_agent


class TestTeacherAgentInterface(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch("teacher_agent_interface.TeacherAgent")
    def test_run_teacher_agent_callable(self, mock_agent_cls):
        mock_instance = mock_agent_cls.return_value
        mock_instance.ask.return_value = "Untouched teacher response"

        result = run_teacher_agent(
            message="Explain photosynthesis.",
            user_id="STUDENT001",
            role="student",
            session_id="test-session-001",
        )
        self.assertEqual(result, "Untouched teacher response")
        mock_instance.ask.assert_called_once_with("Explain photosynthesis.")

    @patch("app.interface.api.TeacherAgent")
    def test_http_endpoint_post_teacher_agent(self, mock_agent_cls):
        mock_instance = mock_agent_cls.return_value
        mock_instance.ask.return_value = "Calculus is the study of continuous change."

        payload = {
            "message": "Explain calculus.",
            "user_id": "STUDENT001",
            "role": "student",
            "session_id": "test-session-001",
        }

        response = self.client.post("/api/teacher-agent", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "Calculus is the study of continuous change.")
        self.assertEqual(data["user_id"], "STUDENT001")
        self.assertEqual(data["role"], "student")
        self.assertEqual(data["session_id"], "test-session-001")


if __name__ == "__main__":
    unittest.main()
