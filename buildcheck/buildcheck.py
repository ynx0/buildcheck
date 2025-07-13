import reflex as rx

from .components.stats_cards import stats_cards_group
import buildcheck.views.employee_upload as em
from buildcheck.views.reviewer_assignment import rv_assignment
from buildcheck.views.admin_dashboard import am_dashboard
from buildcheck.components.navbar import navbar


def index() -> rx.Component:
    return rx.vstack(
        navbar(),
        stats_cards_group(),
        rx.box(
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
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
    em.upload_page,
    title="Employee Dashboard",
    description="This page is where the employee can view their case."
)

app.add_page(rv_assignment, title="Blueprint Assignment")

app.add_page(am_dashboard, title="Admin Dashboard")

