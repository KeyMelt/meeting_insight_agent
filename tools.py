import json
from datetime import datetime

import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from employees import get_email_for_name
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.sent_emails = []
        # Load SMTP config from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.sender_email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")

    def send_email(self, to: str, subject: str, body: str) -> str:
        """
        Sends a real email using SMTP.
        Resolves names to emails using the employee directory first.
        """
        # Resolve 'to' address
        # If it looks like an email, use it. Otherwise, look it up.
        if "@" in to:
            resolved_to = to
        else:
            resolved_to = get_email_for_name(to)
            
        if not resolved_to:
             return f"❌ Failed: Could not resolve email for '{to}'"
        
        email_record = {
            "to": resolved_to,
            "original_to": to,
            "subject": subject,
            "body": body,
            "timestamp": datetime.now().isoformat(),
            "status": "Pending"
        }

        if not self.sender_email or not self.password:
            email_record["status"] = "Failed (Missing Credentials)"
            self.sent_emails.append(email_record)
            return f"❌ Failed to send email to {resolved_to}: Missing SMTP_EMAIL or SMTP_PASSWORD in .env"

        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = resolved_to
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, resolved_to, message.as_string())
            
            email_record["status"] = "Sent"
            self.sent_emails.append(email_record)
            return f"📧 Real email sent to {resolved_to} (Subject: {subject})"
            
        except Exception as e:
            email_record["status"] = f"Error: {str(e)}"
            self.sent_emails.append(email_record)
            return f"❌ Failed to send email to {resolved_to}: {e}"

    def get_sent_emails(self):
        return self.sent_emails

import requests

class TicketService:
    def __init__(self):
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.token = os.getenv("TRELLO_TOKEN")
        self.board_id = os.getenv("TRELLO_BOARD_ID")
        self.list_id = os.getenv("TRELLO_LIST_ID")
        self.base_url = "https://api.trello.com/1"

    def create_ticket(self, title: str, description: str, priority: str = "Medium") -> str:
        """Creates a card in Trello."""
        if not self.api_key or not self.token or not self.list_id:
            return "❌ Failed: Missing Trello credentials (API_KEY, TOKEN, or LIST_ID)."

        url = f"{self.base_url}/cards"
        
        # Map priority to labels (optional, can be expanded)
        # For now, we just append it to the description
        full_desc = f"{description}\n\n**Priority:** {priority}"

        query = {
            'key': self.api_key,
            'token': self.token,
            'idList': self.list_id,
            'name': title,
            'desc': full_desc,
            'pos': 'top'
        }

        try:
            response = requests.request("POST", url, params=query)
            if response.status_code == 200:
                card_data = response.json()
                return f"✅ Trello Card Created: {card_data.get('shortUrl')}"
            else:
                return f"❌ Failed to create card: {response.text}"
        except Exception as e:
            return f"❌ Error connecting to Trello: {str(e)}"

    def get_tickets(self):
        """Fetches cards from the list to show state."""
        if not self.api_key or not self.token or not self.list_id:
            return []
            
        url = f"{self.base_url}/lists/{self.list_id}/cards"
        query = {
            'key': self.api_key,
            'token': self.token
        }
        
        try:
            response = requests.request("GET", url, params=query)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
