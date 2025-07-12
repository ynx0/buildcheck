import reflex as rx
from buildcheck.components.bclogo import bclogo



def footer() -> rx.Component:
    return rx.hstack(
    	bclogo(),
        rx.spacer(),
        rx.text("Made by ARCH Authors", font_size="0.7em", color="gray"),
        rx.spacer(),
        rx.button(
            rx.hstack(
                rx.icon("download"),
                rx.text("Building Guidelines", size="3"),
            ),
            align_self="end",
            mt="1em",
            color_scheme="blue",
            on_click=rx.download(url="/sbc201.pdf")
        ),
        padding="2em",
        spacing="5",
    )