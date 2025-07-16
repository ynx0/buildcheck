import reflex as rx
from datetime import datetime, timedelta  # Importing Python's datetime tools to manage timestamps

# Imporing reusable layout components created by the team 
from buildcheck.components.navbar import navbar_reviewer
from buildcheck.components.footer import footer
from buildcheck.components.notification import notifications_page

# Sample dummy data for the Reviewer 
# Each notification entry includes:
# - title: heading text
# - message: description of what's happening
# - timestamp: when the event occurred
reviewer_notifs = [
    {
        "title": "Blueprint Assigned",
        "message": "You have been assigned to review blueprint no.1.",
        "timestamp": datetime.now() - timedelta(days=2)
    },
    {
        "title": "Pending Compliance Check",
        "message": "Blueprint no.1 is ready for your compliance assessment.",
        "timestamp": datetime.now() - timedelta(days=3, hours=4)
    },
    {
        "title": "Review Completed",
        "message": "You submitted a compliance report for blueprint no.2.",
        "timestamp": datetime.now() - timedelta(days=5)
    },
]

# Main Reviewer page function 
def reviewer_notifications() -> rx.Component:
    return navbar_reviewer(), notifications_page("Reviewer", reviewer_notifs), footer()

