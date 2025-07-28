import os  # For accessing environment variables
from dotenv import load_dotenv  # To load variables from a .env file
import resend  # Resend email service to send emails
from datetime import datetime, timezone  # To work with timezone aware datetimes
import base64  # For encoding attachments
from buildcheck.backend.supabase_client import supabase_client as supabase
from enum import Enum

# Load environment variables from a .env file (for sensitive info like API keys)
load_dotenv()

# Set the Resend API key (used for sending emails)
resend.api_key = os.getenv("RESEND_API_KEY")


class Titles(Enum):
    REVIEW_COMPLETED = "Review completed"
    SUBMISSION_RECIEVED = "Submission received"
    UNDER_REVIEW = "Under Review"

def send_email(user_email, user_name, status, message, approval=False):
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
        # TODO change back to archsystemksa@gmail.com
        "to": [f"yaseen.nvt@gmail.com"],  # Recipient(s) (Arch team only for the time being)
        "subject": subject,
        "html": html_content,
    }

    # If the status is approve, attach the approval letter PDF
    if approval:
        # Open the PDF in binary mode and read its content
        with open("buildcheck/backend/ApprovalLetter.pdf", "rb") as f:
            encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
            # Add attachments to the payload
            email_payload["attachments"] = [
                {
                    "filename": "ApprovalLetter.pdf",
                    "content": encoded_pdf,
                    "type": "application/pdf"  # may help avoid bugs in some APIs
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

def notify_all(title, message, case_id):
    """
    Notifies both the submitter and reviewer of a specific case.

    Args:
        title (str): Notification title (e.g. "Approved", "Rejected").
        message (str): Message body.
        case_id (int): ID of the case to notify its submitter and reviewer.
    """
    # STEP 1: Get the IDs of the submitter and reviewer for the given case
    # This sends a request to the "cases" table in the database to find the row with this case_id,
    # and returns the submitter_id and reviewer_id (which are both user IDs).
    response = supabase.table("cases").select("submitter_id, reviewer_id").eq("id", case_id).single().execute()
    case_data = response.data

    # If no case data is returned (invalid case ID), print an error and stop the function
    if not case_data:
        print(f"[notify_all] No case found with ID {case_id}")
        return
    
    # STEP 2: Create a list of both user IDs so we can fetch their info
    user_ids = [case_data["submitter_id"], case_data["reviewer_id"]]

    # STEP 3: Get the users' details (name and email) using their IDs
    users_response = supabase.table("users").select("id, name, email").in_("id", user_ids).execute()

    # If no user data is returned (e.g., deleted users), stop here
    if not users_response.data:
        print(f"[notify_all] No users found for case ID {case_id}")
        return

    # STEP 4: For each user (submitter and reviewer) we do the following:
    for user in users_response.data:
        # 1. Add a notification to the notifications table in the database
        insert_notification(user["id"], title, message)
        
         # 2. Send them an email with the same title and message
        send_email(user["email"], user["name"], title, message)


if __name__ == '__main__':
    # notify_all(Titles.REVIEW_COMPLETED.value, "The thing worked.", 2)
    send_email("omar@aramco.com", "omar123", "approved yay", "everything is great", approval=True)

