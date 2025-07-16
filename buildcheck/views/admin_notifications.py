import reflex as rx
from datetime import datetime, timedelta  # Importing Python's datetime tools to manage timestamps 

# Imporing reusable layout components created by the team 
from buildcheck.components.navbar import navbar_admin
from buildcheck.components.footer import footer
from buildcheck.components.notification import notifications_page

# Sample dummy data for the Admin 
# Each dictionary represents one notification to show on the admin’s page
admin_notifs = [
    {
        "title": "New Submission Received",
        "message": "A new blueprint has been submitted and is pending assignment to a reviewer.",
        "timestamp": datetime.now() - timedelta(days=1)
    },
    {
        "title": "Review Deadline Approaching",
        "message": "Reminder: Reviewer for blueprint no.1 has 2 days left to complete validation.",
        "timestamp": datetime.now() - timedelta(days=3)
    },
    {
        "title": "Approval Sent",
        "message": "Blueprint no.2 has been approved and a confirmation email was sent to the employee.",
        "timestamp": datetime.now() - timedelta(days=6)
    },
]

# Main Admin page function 
# This function is used by Reflex to display the admin notifications UI
def admin_notifications() -> rx.Component:
    return navbar_admin(), notifications_page("Admin", admin_notifs), footer()

