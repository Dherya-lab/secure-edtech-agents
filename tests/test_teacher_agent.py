import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.agent.teacher_agent import TeacherAgent, ask_teacher
from openai import AuthenticationError


class TestTeacherAgent(unittest.TestCase):

    def test_missing_api_key(self):
        # When no API key is available
        agent = TeacherAgent(api_key="")
        response = agent.ask("Explain photosynthesis.")
        self.assertIn("Error", response)
        self.assertIn("API key not found", response)

    @patch("app.agent.teacher_agent.OpenAI")
    def test_invalid_api_key(self, mock_openai_cls):
        # Simulate authentication error from OpenAI API
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="Incorrect API key provided",
            response=MagicMock(status_code=401),
            body=None,
        )

        agent = TeacherAgent(api_key="sk-invalid-test-key")
        response = agent.ask("What is a Python function?")
        self.assertIn("Error", response)
        self.assertIn("Invalid or unauthorized LLM API key", response)

    @patch("app.agent.teacher_agent.OpenAI")
    def test_normal_educational_question(self, mock_openai_cls):
        # Simulate standard LLM response without tools
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.tool_calls = None
        mock_message.content = "Photosynthesis is the process by which green plants convert sunlight into chemical energy."

        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client.chat.completions.create.return_value = mock_response

        agent = TeacherAgent(api_key="sk-valid-mock-key")
        response = agent.ask("Explain photosynthesis.")
        self.assertEqual(response, "Photosynthesis is the process by which green plants convert sunlight into chemical energy.")
        mock_openai_cls.assert_called_once_with(
            api_key="sk-valid-mock-key",
            base_url="https://openrouter.ai/api/v1",
        )

    @patch("app.agent.teacher_agent.OpenAI")
    def test_agent_using_education_tool(self, mock_openai_cls):
        # Simulate tool call to get_student_courses
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        # First call returns a tool call request
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_abc123"
        mock_tool_call.function.name = "get_student_courses"
        mock_tool_call.function.arguments = '{"student_id": "S101"}'

        first_message = MagicMock()
        first_message.tool_calls = [mock_tool_call]
        first_message.content = None

        first_choice = MagicMock()
        first_choice.message = first_message
        first_response = MagicMock()
        first_response.choices = [first_choice]

        # Second call returns the final text incorporating tool results
        second_message = MagicMock()
        second_message.tool_calls = None
        second_message.content = "Student S101 is enrolled in CS101, MATH201, and SEC301."

        second_choice = MagicMock()
        second_choice.message = second_message
        second_response = MagicMock()
        second_response.choices = [second_choice]

        mock_client.chat.completions.create.side_effect = [first_response, second_response]

        agent = TeacherAgent(api_key="sk-valid-mock-key")
        response = agent.ask("What courses is student S101 enrolled in?")
        self.assertIn("enrolled in CS101", response)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)


if __name__ == "__main__":
    unittest.main()
