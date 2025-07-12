import reflex as rx
from buildcheck.components.bclogo import bclogo


def footer() -> rx.Component:
    return rx.box(
        rx.vstack(
            bclogo(),
            rx.spacer(),
            rx.text("© 2025  Inc. • Privacy • Terms "),
            rx.spacer(),
            rx.button(
                rx.hstack(
                    rx.icon("download"),
                    rx.text("Building Guidelines", size="3"),
                ),
                mt="1em",
                color_scheme="blue",
                on_click=rx.download(url="/sbc201.pdf")
            ),
            padding="2em",
            spacing="3",
            align="center"
        ),
        width="100%"
    )
