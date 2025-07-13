import reflex as rx
from .navbar import navbar

def employee_blueprint1() -> rx.Component:
    return rx.vstack(
        #navbar(),
        rx.heading("Overall Summary"),
        rx.button("Click Me", color_scheme="blue"),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    )   