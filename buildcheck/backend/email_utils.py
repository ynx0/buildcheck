import os # For accessing environment variables
from dotenv import load_dotenv # To load variables from a .env file
from supabase import create_client # Supabase client to interact with the database
import resend # Resend email service to send emails
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set Resend API key for sending email to admin
resend.api_key = os.getenv("RESEND_API_KEY")

# This function sends an email to inform someone their case was approved/rejected.
def send_email(user_email: str, user_name: str, case_id: int, status: str, comments: str = "") -> bool:
    """
    Sends an email using Resend API to my personal email (due to domain restrictions).
    Returns True if successful, False if failed.
    """
    try:
    # Construct the subject and HTML content [f] is for using a variable inside a string such as {user_email}
        subject = f"Case {status.capitalize()} – ID {case_id}"

        html_content = f"""
        <div style='font-family: Arial;'>
            <h2>ARCH System Notification</h2>
            <p><strong>Employee:</strong> {user_name} ({user_email})</p>
            <p><strong>Case ID:</strong> {case_id}</p>
            <p><strong>Status:</strong> {status.upper()}</p>
            {f'<p><strong>Comments:</strong> {comments}</p>' if comments else ''}
            <p>This message was sent to admin only (due to domain restrictions).</p>
        </div>
        """

        # Send email using Resend (goes only to my personal email address)
        resend.Emails.send({
            "from": "ARCH System <onboarding@resend.dev>",
            "to": ["nouranasir33@gmail.com"],
            "subject": subject,
            "html": html_content,
        })

        print("Email sent to admin.")
        return True

    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

# Function to insert notification in Supabase 'notifications' table
# This will show up in the frontend UI for the employee
def insert_notification(user_id: int, title: str, message: str) -> bool:
    try:
        result = supabase.table("notifications").insert({
            "user_id": user_id,
            "title": title,
            "message": message,
            "read": False,  # default unread
            "created_at": datetime.now(timezone.utc).isoformat(),  # use timezone-aware UTC datetime
        }).execute()

        print("Notification inserted to DB!")
        return True

    except Exception as e:
        print(f"Failed to insert notification: {e}")
        return False

# Function to notify approval
def notify_approval(case_id: int, comments: str = "") -> bool:
    return _notify_case_status(case_id=case_id, status="approved", comments=comments)

# Function to notify rejection
def notify_rejection(case_id: int, comments: str = "") -> bool:
    return _notify_case_status(case_id=case_id, status="rejected", comments=comments)

# Shared internal helper for both approve and reject flows
def _notify_case_status(case_id: int, status: str, comments: str = "") -> bool:
    try:
        # Fetch case info
        case_response = supabase.table("cases").select("*").eq("id", case_id).execute()
        if not case_response.data:
            print(f"No case found with ID {case_id}")
            return False

        case = case_response.data[0]
        submitter_id = case.get("submitter_id")

        # Fetch user info
        user_response = supabase.table("users").select("*").eq("id", submitter_id).execute()
        if not user_response.data:
            print(f"No user found with ID {submitter_id}")
            return False

        user = user_response.data[0]

        # Send email to admin (my email)
        send_email( 
            user_email=user["email"],
            user_name=user["name"],
            case_id=case_id,
            status=status,
            comments=comments,
        )

        # Create notification message for the user (in-app)
        message = f"Your blueprint (ID: {case_id}) is {status}."
        if comments:
            message += f" Comments: {comments}"
        title = f"Blueprint {status.capitalize()}"

        # Insert notification into database
        insert_notification(
            user_id=submitter_id,
            title=title,
            message=message,
        )

        return True

    except Exception as e:
        print(f"Error in _notify_case_status: {e}")
        return False

# Notify reviewer when assigned a case
def assign_case_and_notify(case_id: int, reviewer_id: int) -> bool:
    try:
        # Update reviewer_id in cases table
        supabase.table("cases").update({"reviewer_id": reviewer_id}).eq("id", case_id).execute()

        # Get reviewer details
        reviewer_resp = supabase.table("users").select("*").eq("id", reviewer_id).execute()
        if not reviewer_resp.data:
            print(f"No reviewer with ID {reviewer_id}")
            return False 

        reviewer = reviewer_resp.data[0]
    
        # Insert notification for the reviewer
        return insert_notification(
            user_id=reviewer_id,
            title="New Case Assigned",
            message=f"You have been assigned to review case ID {case_id}.",
        )

    except Exception as e:
        print(f"Failed to assign and notify reviewer: {e}")
        return False

