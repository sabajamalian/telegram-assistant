from typing import Dict, Any, Tuple
import openai
from . import email_rojin, email_saba, email_baroj_events, reminder

class TaskManager:
    def __init__(self, openai_client):
        """Initialize the task manager with OpenAI client."""
        self.client = openai_client

    async def process_task(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process the text to identify and execute the appropriate task.
        
        Args:
            text (str): The processed text from voice message
            
        Returns:
            Tuple[str, Dict[str, Any]]: Task type and response
        """
        # Use ChatGPT to identify the task
        task_prompt = f"""Analyze the following text and identify which task is being requested. 
        The possible tasks are:
        1. Send an email to Rojin
        2. Send an email to Saba
        3. Send an email to Baroj Events
        4. Set a reminder

        Text: {text}

        Respond with ONLY the task number (1-4) and nothing else."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a task classifier. Your job is to identify which task is being requested from the given text."},
                {"role": "user", "content": task_prompt}
            ],
            temperature=0.1
        )

        task_number = response.choices[0].message.content.strip()
        
        # Execute the appropriate task
        if task_number == "1":
            return "email_rojin", await email_rojin.send_email_rojin(text)
        elif task_number == "2":
            return "email_saba", await email_saba.send_email_saba(text)
        elif task_number == "3":
            return "email_baroj_events", await email_baroj_events.send_email_baroj_events(text)
        elif task_number == "4":
            return "reminder", await reminder.set_reminder(text)
        else:
            return "unknown", {
                "status": "error",
                "message": "Could not identify the requested task",
                "content": text
            } 