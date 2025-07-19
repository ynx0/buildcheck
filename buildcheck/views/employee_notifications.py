import reflex as rx  
from datetime import datetime, timedelta # Importing Python's datetime tools to manage timestamps 

# Imporing reusable layout components created by the team 
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.notification import notifications_page

# Sample dummy data for the Employee 
# Each dictionary represents one notification to show on the admin’s page
employee_notifs = [
    {
        "title": "Submission Received",
        "message": "Your blueprint no.1 has been received successfully and is now pending review!",
        "timestamp": datetime.now() - timedelta(days=2)
    },
    {
        "title": "Under Review",
        "message": "Your blueprint no.1 is currently being reviewed!",
        "timestamp": datetime.now() - timedelta(days=4)
    },
    {
        "title": "Review Completed with Issues",
        "message": "Your blueprint no.1 has been completed! Please review the attached compliance report for a detailed overview of the results.",
        "timestamp": datetime.now() - timedelta(days=5, hours=6)
    },
]

# Render the employee notifications page using the reusable component
def employee_notifications() -> rx.Component:
    return rx.vstack(
        navbar(),
        notifications_page("Employee", employee_notifs),
        footer()
    )
