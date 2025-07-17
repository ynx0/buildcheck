import reflex as rx



def bclogo() -> rx.Component:
    return rx.hstack(
        rx.image(
            src="/logo.png",
            width="auto",
            height="100px",
        ),
        # rx.heading("ARCH", size="6"),
        # align="center"
    )