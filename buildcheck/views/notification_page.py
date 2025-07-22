import reflex as rx
from datetime import datetime
from typing import List, Dict
from buildcheck.backend.supabase_client import supabase_client
# Importing reusable layout components created by the team 
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.notification import notifications_page # Import the UI component that displays notifications
from buildcheck.state.user_state import UserState # Import global user state (which stores logged in user data like name, role, id, etc.)


# 1. Define Notification State to track user info and hold fetched notifications
class NotificationState(UserState):
    # List to store all notifications fetched from database
    notifications: list[dict] = []

    @rx.var
    def role_heading(self) -> str:
        """Create a properly formatted heading based on user's role"""
        # Capitalize the role for heading (e.g., "Admin", "Reviewer")
        return self.role.capitalize() if self.role else ""

    @rx.var
    def footer_component(self) -> rx.Component:
        """Return the footer component for the page"""
        return footer()

    @rx.var
    def has_notifications(self) -> bool:
        """Check if user has any notifications to display"""
        return len(self.notifications) > 0

    @rx.event
    def load_notifications(self):
        """Fetch all notifications for the current logged-in user from database"""
        try:
            # Query our database for notifications belonging to current user
            response = supabase_client.table("notifications") \
                .select("*") \
                .eq("user_id", self.user_id) \
                .order("created_at", desc=True) \
                .execute()

            # Store the fetched notifications in state for display
            self.notifications = response.data
            
        except Exception as e:
            # Print error message if database query fails
            print("Failed to load notifications:", e)


# 2. Notifications Page View - Main page component
@rx.page(route="/notifications-page", title="Notifications")
def notifications_page_view() -> rx.Component:
    """Create the complete notifications page layout"""
    return rx.fragment(
        # Top navigation bar
        navbar(),
        # Main content area centered on page
        rx.center(
            rx.vstack(
                # Page title
                rx.heading("Notifications Center", size="6"),
                # Conditionally show notifications or "no notifications" message
                rx.cond(
                    NotificationState.has_notifications,
                    notifications_page(NotificationState.role_heading, NotificationState.notifications),
                    rx.text("No notifications to display."),
                ),
                padding="2em",
            ),
        ),
        # Footer at bottom of page
        NotificationState.footer_component,
        # Automatically load notifications when page loads
        on_mount=NotificationState.load_notifications,
    )