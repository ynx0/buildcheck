import os  # For accessing environment variables
from dotenv import load_dotenv  # To load variables from a .env file
from supabase import create_client  # To interact with the database
import resend  # Resend email service to send emails
from datetime import datetime, timezone  # To work with timezone aware datetimes

# Load environment variables from a .env file (for sensitive info like API keys)
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Initialize the Supabase client using the credentials
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set the Resend API key (used for sending emails)
resend.api_key = os.getenv("RESEND_API_KEY")

def send_email(user_email, user_name, status, message):
    """
    Sends an email to the user with their approval or rejection status.
    If status is approved, it attaches ApprovalLetter.pdf to the email.
    """
    subject = f"Notification: {status}"  # Email subject
    # Email body as HTML
    html_content = f"""
    <div>
        <h2>ARCH System Notification</h2>
        <p><strong>User:</strong> {user_name} ({user_email})</p>
        <p><strong>Status:</strong> {status.upper()}</p>
        <p>{message}</p>
    </div>
    """

    # To prepare the email details in a dictionary (payload)
    email_payload = {
        "from": "ARCH System <onboarding@resend.dev>",  # Sender email
        "to": ["archsystemksa@gmail.com"],  # Recipient(s) (Arch team only for the time being)
        "subject": subject,
        "html": html_content,
    }

    # If the status is approve, attach the approval letter PDF
    if status.lower() == "approve":
        # Open the PDF in binary mode and read its content
        with open("ApprovalLetter.pdf", "rb") as f:
            # Add attachments to the payload
            email_payload["attachments"] = [
                {
                    "filename": "ApprovalLetter.pdf",
                    "content": f.read(),
                }
            ]

    # Send the email using Resend
    resend.Emails.send(email_payload)

def insert_notification(user_id, title, message):
    """
    Inserts a notification for a user into the 'notifications' table in the DB.
    This will appear in the frontend UI for the employee.
    """
    supabase.table("notifications").insert({
        "user_id": user_id,
        "title": title,
        "message": message,
        "read": False,  # Mark as unread by default
        "created_at": datetime.now(timezone.utc).isoformat(),  # Store current UTC time
    }).execute()

def notify_all_roles(title, message):
    """
    Sends an email and inserts a notification for every user role (admin, employee, reviewer).
    For each user, an internal notification is inserted, and an email is sent.
    """
    roles = ["admin", "employee", "reviewer"]  # Roles to notify
    for role in roles:
        # Query all users in the 'users' table with the current role
        users_resp = supabase.table("users").select("*").eq("role", role).execute()
        if users_resp.data:  # If there are users for this role
            for user in users_resp.data: # Loop through each user in the result
                insert_notification(user["id"], title, message)  # Add notification to DB
                send_email(user["email"], user["name"], title, message)  # Send email notification