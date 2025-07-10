import reflex as rx

from .components.stats_cards import stats_cards_group
import buildcheck.components.employee_upload as em
from .views.navbar import navbar
from .views.table import main_table


def index() -> rx.Component:
    return rx.vstack(
        navbar(),
        stats_cards_group(),
        rx.box(
            main_table(),
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    )


def upload() -> rx.Component:
    return rx.vstack(
        em.navbar(),
        rx.center(
            em.upload_card(),
            padding_y="4em"
        ),
        rx.heading("Recent Upload Activity", size="9", mt="3em"),
        em.upload_table(),
        em.footer(),
        spacing="3",
        align="center",
        padding="3",
    )



app = rx.App(
    theme=rx.theme(
        appearance="light", has_background=True, radius="large",
        # accent_color="grass"
    ),
)

app.add_page(
    index,
    title="Customer Data App",
    description="A simple app to manage customer data.",
)


app.add_page(
    upload,
    title="Employee Dashboard",
    description="This page is where the employee can view their case."
)

