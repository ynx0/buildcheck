import reflex as rx
from buildcheck.components.bclogo import bclogo
from buildcheck.state.user_state import UserState

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            bclogo(),
            rx.spacer(),
            # Conditionally render links based on role
            rx.cond(
                UserState.role == "employee",
                rx.fragment(
                    rx.link("Home", href="/upload"),
                    rx.link("Status", href="/blueprint-pending"),
                ),
                rx.cond(
                    UserState.role == "admin",
                    rx.fragment(
                        rx.link("Dashboard", href="/admin-dashboard"),
                        rx.link("Assignments", href="/admin-assignments"),
                    ),
                    rx.cond(
                        UserState.role == "reviewer",
                        rx.fragment(
                            rx.link("Home", href="/assignments"),
                            rx.link("Report Viewer", href="/validation"),
                        ),
                        rx.fragment()  # Default: no links
                    )
                )
            ),
            rx.spacer(),
            rx.button(
                "Logout", 
                size="3", 
                variant="outline",
                on_click=UserState.handle_logout
            ),
            rx.icon_button(rx.icon("bell"), on_click=rx.redirect("/notifications-page"), variant="ghost"),
            rx.avatar(
                fallback=UserState.nameIntials,
                size="3"
            ),
            padding="1em",
            border_bottom="1px solid #eee",
            align="center"
        ),
        width="100%"
    )