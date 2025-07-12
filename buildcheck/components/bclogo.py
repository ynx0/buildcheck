import reflex as rx



def bclogo() -> rx.Component:
    return rx.hstack(
        rx.image(
            src="/arch_logo.png",
            width="auto",
            height="50px",
        ),
        rx.heading("BuildCheck", size="6"),
        align="center"
    )