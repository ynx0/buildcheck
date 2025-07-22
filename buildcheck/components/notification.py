import reflex as rx  # Reflex for building UI components

# 1. Format timestamp strings for display 
def format_timestamp(timestamp_str: str) -> str:
    """Convert database timestamp string to readable format"""
    try:
        # Parse the timestamp string from database
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Return formatted date and time
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        # Return original string if parsing fails
        return timestamp_str


# 2. Single Notification Card Component (larger size)
def notification_card(title: str, message: str, timestamp: str) -> rx.Component:
    """Create individual notification card with title, message, and timestamp"""
    return rx.box(
        rx.hstack(
            # Left side: notification content
            rx.vstack(
                # Bold notification title
                rx.text(title, weight="bold", size="4"), 
                # Notification message text
                rx.text(message, size="3"), 
                align_items="start",
                spacing="2",
            ),
            # Push timestamp to the right side
            rx.spacer(),
            # Right side: formatted timestamp
            rx.text(
                format_timestamp(timestamp), 
                size="2",  
                color="gray"
            ),
            align_items="start",
        ),
        # Card styling: larger padding for bigger appearance
        border="1px solid #CBD5E0",
        border_radius="md", 
        padding="1.5em",  
        background_color="#F8FAFC",
        margin_bottom="1em",
        width="100%",
        min_height="80px",  # Ensure minimum card height
    )


# 3. Notifications Page Layout
def notifications_page(role: str, notifications: list[dict]) -> rx.Component:
    """Create the main notifications display area with header and notification list"""
    return rx.container(
        # Header with bell icon and role-specific title
        rx.hstack(
            rx.heading(f"{role} Notifications", size="5"),
            spacing="3",
            margin_bottom="1em"
        ),

        # Search input (UI only, non-functional)
        rx.input(
            placeholder="Search notifications...",
            width="300px",
            margin_bottom="1.5em"
        ),

        # Display each notification using the notification_card component
        rx.foreach(
            notifications, 
            lambda item: notification_card(
                item["title"], 
                item["message"], 
                item["created_at"]  # Use created_at field for timestamp
            )
        ),
        padding="2em",
        max_width="800px",  # Limit container width for better readability
    )