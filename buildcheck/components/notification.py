import reflex as rx  # Import the Reflex library to build UI components
from datetime import datetime  # Importing Python's datetime tools to manage timestamps 

# FUNCTION 1 
# A helper function to format the timestamp in a readable way
# For example: "Fri, Sep 15, 08:00 AM (2 days ago)"
def format_datetime(dt: datetime) -> str:
    return dt.strftime("%a, %b %d, %I:%M %p") + f" ({(datetime.now() - dt).days} days ago)"

# FUNCTION 2
# This function defines a reusable like the (notification card)
# A "component" in Reflex is like a building block (like a box or button) used to create the web interface
# Parameters:  
# - title: The heading of the notification (e.g., "Submission Received")
# - message: The body text (e.g., "Your blueprint has been received.")
# - timestamp: The time the notification was created
def notification_card(title: str, message: str, timestamp: datetime) -> rx.Component:
    return rx.box(  # This box is the outer card for one notification
        rx.hstack(  # A horizontal layout to show message on the left and timestamp on the right
            rx.vstack(  # Stack title and message vertically
                rx.text(title, weight="bold"),  # Notification title in bold
                rx.text(message, size="2"),     # Notification message below the title
            ),
            rx.spacer(),  # Pushes timestamp all the way to the right
            rx.text(format_datetime(timestamp), size="1"),  # Formatted date text
        ),
        border="1px solid #CBD5E0",  # Light border around the notification
        border_radius="md",          # Medium rounded corners
        padding="1em",               # Internal spacing inside the box
        background_color="#F8FAFC",  # Light gray background
        margin_bottom="1em"          # Space below each notification
    )

# FUNCTION 3 
# This function builds the entire notifications page for any user type
# It takes in:
# - role: The user role ("Employee", "Admin", & "Reviewer") to customize the page heading
# - notifications: A list of dictionaries with title, message, and timestamp for each notification
def notifications_page(role: str, notifications: list[dict]) -> rx.Component:
    return rx.container(  # This wraps the entire page content

        # Page Header with Bell Icon and Heading 
        rx.hstack(
            rx.icon(tag="bell"),  # Bell icon on the left
            rx.heading(f"{role} Notifications", size="6"),  # Heading with the user's role
            spacing="3",
            margin_bottom="1em"
        ),

        # Search Bar (It is non-functioning, so UI only for now) 
        rx.input(
            placeholder="Search",  # Placeholder text inside the search box
            width="300px",         # Width of the search field
            margin_bottom="1.5em"  # Space below the input
        ),

        # List of Notifications 
        # For each notification in the list, generate a styled card using notification_card()
        *[notification_card(n["title"], n["message"], n["timestamp"]) for n in notifications],

        padding="2em"  # Add space around the whole page for better layout
    )
