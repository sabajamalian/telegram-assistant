from typing import Dict, Any, Tuple
import openai
import json
from datetime import datetime
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
        # Get current date and time
        current_datetime = datetime.now().isoformat()
        
        # Use ChatGPT to identify the task
        task_prompt = f"""You are a smart assistant. The current date and time is {current_datetime} Your job is to understand a natural language instruction in any language and classify it as one of the following tasks:

---

1. Task: send_email  
Description: The user wants to send an email to someone. Your job is to identify the recipient from the text and also interpret what the user wants to write in the email.
Valid recipients: "saba", "rojin", "baroj events"  
Expected format:
{{
  "task": "send_email",
  "params": {{
    "to": "saba" | "rojin" | "baroj events",
    "content": "the content of the email"
  }}
}}

---

2. Task: add_to_list  
Description: The user wants to add an item to a list.  
Examples: "bananas to shopping list", "milk to grocery list"  
Expected format:
{{
  "task": "add_to_list",
  "params": {{
    "item": "bananas",
    "list": "shopping list"
  }}
}}

---

3. Task: set_reminder  
Description: The user wants to set a reminder for a specific topic at a certain time.  
Expected format:
{{
  "task": "set_reminder",
  "params": {{
    "topic": "pick up kids",
    "time": "2025-05-27T17:00:00"  // ISO 8601 preferred, or natural language like "tomorrow at 5pm"
  }}
}}

---

If the input does not match any task, reply with:
{{
  "task": "unknown",
  "params": {{}}
}}

Only output JSON. Do not explain or say anything else.

Input text: {text}"""

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a task classifier that understands both English and Farsi. Your job is to identify which task is being requested from the given text and output the result in JSON format. Be tolerant of minor errors and use your best judgment to infer user intent."},
                {"role": "user", "content": task_prompt}
            ],
            temperature=0.1
        )

        try:
            # Parse the JSON response
            task_data = json.loads(response.choices[0].message.content.strip())
            task_type = task_data["task"]
            params = task_data["params"]

            # Execute the appropriate task
            if task_type == "send_email":
                recipient = params["to"]
                email_content = params["content"]
                if recipient == "rojin":
                    result = await email_rojin.send_email_rojin(email_content)
                    result.update({
                        "task_type": task_type,
                        "parameters": params
                    })
                    return "email_rojin", result
                elif recipient == "saba":
                    result = await email_saba.send_email_saba(email_content)
                    result.update({
                        "task_type": task_type,
                        "parameters": params
                    })
                    return "email_saba", result
                elif recipient == "baroj_events":
                    result = await email_baroj_events.send_email_baroj_events(email_content)
                    result.update({
                        "task_type": task_type,
                        "parameters": params
                    })
                    return "email_baroj_events", result
            elif task_type == "add_to_list":
                # TODO: Implement add_to_list functionality
                return "add_to_list", {
                    "status": "success",
                    "message": f"Added {params['item']} to {params['list']}",
                    "content": text,
                    "task_type": task_type,
                    "parameters": params
                }
            elif task_type == "set_reminder":
                result = await reminder.set_reminder(text)
                result.update({
                    "task_type": task_type,
                    "parameters": params
                })
                return "reminder", result
            else:
                return "unknown", {
                    "status": "error",
                    "message": "Could not identify the requested task",
                    "content": text,
                    "task_type": task_type,
                    "parameters": params
                }
        except (json.JSONDecodeError, KeyError) as e:
            return "error", {
                "status": "error",
                "message": f"Error processing task: {str(e)}",
                "content": text,
                "task_type": "error",
                "parameters": {}
            } 