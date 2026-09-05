import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env (and .env.txt fallback on Windows)
load_dotenv(project_root / ".env")
if not os.getenv("OPENROUTER_API_KEY"):
    load_dotenv(project_root / ".env.txt")

try:
    from openai import APIConnectionError, APIError, AuthenticationError, OpenAI
except ImportError:
    OpenAI = None
    AuthenticationError = Exception
    APIConnectionError = Exception
    APIError = Exception

from app.tools.education_tools import get_course, get_student, get_student_courses

# Tool definitions for LLM function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_student",
            "description": "Retrieve basic profile information about a student using their student ID (e.g., 'S101').",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "The unique ID of the student, e.g., 'S101'.",
                    }
                },
                "required": ["student_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_student_courses",
            "description": "Retrieve course enrollment records, marks, grades, and attendance for a student using their student ID (e.g., 'S101').",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "The unique ID of the student, e.g., 'S101'.",
                    }
                },
                "required": ["student_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_course",
            "description": "Retrieve course details including course name and instructor name using a course ID (e.g., 'CS101').",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_id": {
                        "type": "string",
                        "description": "The course code, e.g., 'CS101', 'MATH201', 'SEC301'.",
                    }
                },
                "required": ["course_id"],
            },
        },
    },
]

TOOL_MAP = {
    "get_student": get_student,
    "get_student_courses": get_student_courses,
    "get_course": get_course,
}

SYSTEM_INSTRUCTION = (
    "You are a helpful educational teacher. Explain concepts clearly and help students with coursework. "
    "You can use the available education tools when student or course information is required."
)


DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class TeacherAgent:
    """Teacher Agent for the educational framework."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = OPENROUTER_BASE_URL,
        model: Optional[str] = None,
        system_instruction: str = SYSTEM_INSTRUCTION,
    ):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url
        self.model = model or os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
        self.system_instruction = system_instruction

    def ask(self, question: str) -> str:
        """Process a student's question and return the Teacher Agent's response."""
        if OpenAI is None:
            return "Error: The 'openai' package is not installed. Please install it using 'pip install openai'."

        if not self.api_key or self.api_key.strip() == "":
            return (
                "Error: LLM API key not found. Please set OPENROUTER_API_KEY in your .env file or environment variables."
            )

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            messages = [
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": question},
            ]

            max_steps = 5
            for _ in range(max_steps):
                # Call LLM with retry for transient 429 rate limits
                response = None
                for attempt in range(3):
                    try:
                        response = client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            tools=TOOLS,
                            tool_choice="auto",
                        )
                        break
                    except APIError as api_err:
                        status = getattr(api_err, "status_code", None)
                        if status == 429 and attempt < 2:
                            time.sleep(1.5 * (attempt + 1))
                            continue
                        raise api_err

                response_message = response.choices[0].message

                # If no tool calls were requested, return the final answer
                if not response_message.tool_calls:
                    return response_message.content or ""

                # Append assistant's tool-calling message to history
                messages.append(response_message)

                # Execute requested tool calls
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    func = TOOL_MAP.get(func_name)

                    if func:
                        try:
                            func_args = json.loads(tool_call.function.arguments)
                        except Exception:
                            func_args = {}
                        tool_result = func(**func_args)
                    else:
                        tool_result = {
                            "error": f"Tool '{func_name}' is not recognized."
                        }

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": func_name,
                            "content": json.dumps(tool_result),
                        }
                    )

            return response_message.content or ""

        except AuthenticationError:
            return "Error: Invalid or unauthorized LLM API key. Please check your OPENROUTER_API_KEY."
        except APIConnectionError:
            return (
                "Error: Could not connect to OpenRouter API. Please check your network connection."
            )
        except APIError as e:
            return f"Error: OpenRouter API error: {e.message}"
        except Exception as e:
            return f"Error: An unexpected error occurred: {str(e)}"


def ask_teacher(question: str) -> str:
    """Convenience function that accepts a student's question and returns the Teacher Agent's response."""
    agent = TeacherAgent()
    return agent.ask(question)


if __name__ == "__main__":
    print("--- Teacher Agent Demo ---")
    demo_question = "What is a Python function?"
    print(f"Student: {demo_question}")
    reply = ask_teacher(demo_question)
    print(f"Teacher Agent: {reply}")
