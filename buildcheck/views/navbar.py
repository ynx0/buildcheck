import reflex as rx
from buildcheck.components.bclogo import bclogo



def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            bclogo(),
            rx.spacer(),
            rx.link("Home", href="/"),
            rx.link("Status", href="/status"),
            rx.spacer(),
            rx.button("Logout", size="3", variant="outline"),
            rx.icon_button(rx.icon("bell"), variant="ghost"),
            rx.avatar(fallback="PV", size="3"),
            padding="1em",
            border_bottom="1px solid #eee",
            align="center"
        ),
        width="100%"
    )
