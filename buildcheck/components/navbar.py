import reflex as rx
from buildcheck.components.bclogo import bclogo
from buildcheck.state.user_state import UserState

def navbar_employee() -> rx.Component:
    return rx.box(
        rx.hstack(
            bclogo(),
            rx.spacer(),
            rx.link("Home", href="/upload"),
            rx.link("Status", href="/blueprint-pending"),
            rx.spacer(),
            rx.button(
                "Logout", 
                size="3", 
                variant="outline",
                on_click=UserState.handle_logout
            ),
            rx.icon_button(rx.icon("bell"), on_click=rx.redirect("/employee-notifcations"),variant="ghost"),
            rx.avatar(
                fallback=UserState.nameIntials,  # Use initials from global state
                size="3"
            ),
            padding="1em",
            border_bottom="1px solid #eee",
            align="center"
        ),
        width="100%"
    )

def navbar_admin() -> rx.Component:
    return rx.box(
        rx.hstack(
            bclogo(),
            rx.spacer(),
            rx.link("Dashboard", href="/admin-dashboard"),
            rx.link("Assignments", href="/assignments"), # This needs to be changed
            rx.spacer(),
            rx.button(
                "Logout", 
                size="3", 
                variant="outline",
                on_click=UserState.handle_logout
            ),
           rx.icon_button(
            rx.icon("bell"), 
            on_click=rx.redirect("/admin-notifications"), 
            variant="ghost"
            ),
            rx.avatar(fallback=UserState.nameIntials, size="3"),
            padding="1em",
            border_bottom="1px solid #eee",
            align="center"
        ),
        width="100%"
    )


def navbar_reviewer() -> rx.Component:
    return rx.box(
        rx.hstack(
            bclogo(),
            rx.spacer(),
            rx.link("Home", href="/assignments"),
            rx.link("Report Viewer", href="/validation"),
            rx.spacer(),
            rx.button(
                "Logout", 
                size="3", 
                variant="outline",
                on_click=UserState.handle_logout
            ),
            rx.icon_button(rx.icon("bell"), on_click=rx.redirect("/reviewer-notifications"),variant="ghost"),
            rx.avatar(fallback=UserState.nameIntials, size="3",  on_click=UserState.handle_logout),
            padding="1em",
            border_bottom="1px solid #eee",
            align="center"
        ),
        width="100%"
    )