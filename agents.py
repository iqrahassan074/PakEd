import os
from typing import List
import openai
from config import DEFAULT_MODEL
from guardrails import sanitize_output

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SubjectAgent:
    def __init__(self, board: str, subject: str, model: str = DEFAULT_MODEL):
        self.board = board
        self.subject = subject
        self.model = model

    def build_system_prompt(self, language="English"):
        """
        Build a system prompt that instructs the agent to respond in the correct language.
        """
        if language == "Urdu":
            lang_instruction = "Answer in simple Urdu (use Roman Urdu if user types in Roman letters)."
        else:
            lang_instruction = "Answer in clear English."

        return (
            f"You are a helpful Pakistani education assistant specialized in {self.subject} "
            f"for students of the {self.board}. {lang_instruction} "
            "If student asks for exam solutions, give conceptual help, do not provide leaked exam answers."
        )

    def ask(self, user_message: str, history: List[dict] = None) -> str:
      
        if user_message.startswith("[Urdu]"):
            language = "Urdu"
            message_content = user_message.replace("[Urdu]", "").strip()
        else:
            language = "English"
            message_content = user_message.replace("[English]", "").strip()

      
        messages = [{"role": "system", "content": self.build_system_prompt(language)}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message_content})

        resp = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        text = resp.choices[0].message.content
        return sanitize_output(text)


class ExpertAgent:
    """Fallback expert — broader knowledge and more tokens if needed."""
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def ask(self, prompt: str):
      
        if prompt.startswith("[Urdu]"):
            language = "Urdu"
            message_content = prompt.replace("[Urdu]", "").strip()
        elif prompt.startswith("[English]"):
            language = "English"
            message_content = prompt.replace("[English]", "").strip()
        else:
            language = "English"
            message_content = prompt

     
        if language == "Urdu":
            system_prompt = "You are an expert tutor. Answer in simple Urdu."
        else:
            system_prompt = "You are an expert tutor. Answer in English."

        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_content}
            ]
        )
        return sanitize_output(resp.choices[0].message.content)

