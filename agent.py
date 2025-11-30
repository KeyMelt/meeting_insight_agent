import os
import google.generativeai as genai
from tools import EmailService, TicketService
import json

class MeetingAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.email_service = EmailService()
        self.ticket_service = TicketService()

    def analyze_transcript(self, transcript: str):
        """
        Analyzes the transcript to identify action items and decisions.
        Returns a structured JSON response.
        """
        prompt = f"""
        You are an expert executive assistant. Analyze the following meeting transcript.
        Identify key decisions made and specific action items.
        For each action item, determine if it requires an email or a ticket.
        
        Transcript:
        {transcript}
        
        Output must be a valid JSON object with the following structure:
        {{
            "summary": "Brief summary of the meeting",
            "decisions": ["List of decisions"],
            "action_items": [
                {{
                    "description": "What needs to be done",
                    "assignee": "Who is responsible (if known, else 'Unknown')",
                    "type": "email" or "ticket" or "note",
                    "details": {{
                        "to": "email address if type is email",
                        "subject": "email subject if type is email",
                        "body": "email body if type is email",
                        "title": "ticket title if type is ticket",
                        "priority": "High/Medium/Low if type is ticket"
                    }}
                }}
            ]
        }}
        """
        
        response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"Failed to parse model response: {e}", "raw_response": response.text}

    def execute_actions(self, action_items):
        """
        Executes the actions (sending emails, creating tickets) based on the analysis.
        """
        results = []
        for item in action_items:
            action_type = item.get("type")
            details = item.get("details", {})
            
            if action_type == "email":
                res = self.email_service.send_email(
                    to=details.get("to", "unknown@example.com"),
                    subject=details.get("subject", "Action Item"),
                    body=details.get("body", item.get("description"))
                )
                results.append(res)
            elif action_type == "ticket":
                res = self.ticket_service.create_ticket(
                    title=details.get("title", item.get("description")),
                    description=item.get("description"),
                    priority=details.get("priority", "Medium")
                )
                results.append(res)
            else:
                results.append(f"Note recorded: {item.get('description')}")
        return results
