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
        # Resolve 'to' address (e.g., "Alice" -> "alice@example.com")
        resolved_to = get_email_for_name(to)
        
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

class TicketService:
    def __init__(self):
        self.tickets = []
        self.counter = 1

    def create_ticket(self, title: str, description: str, priority: str = "Medium") -> str:
        """Simulates creating a Jira/Support ticket."""
        ticket = {
            "id": f"TICKET-{self.counter}",
            "title": title,
            "description": description,
            "priority": priority,
            "status": "Open",
            "timestamp": datetime.now().isoformat()
        }
        self.tickets.append(ticket)
        self.counter += 1
        return f"Ticket {ticket['id']} created: {title}"

    def get_tickets(self):
        return self.tickets
