import reflex as rx
import reflex_enterprise as rxe

from .components.stats_cards import stats_cards_group
from .views.navbar import navbar
from .views.table import main_table
from .views.employee_view import employee_view
from buildcheck.views.admin_assignments import assignments_table

config = rxe.Config(
    app_name="buildcheck",
    show_built_with_reflex=False,
    use_single_port=True,
)

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


app = rxe.App()

app.add_page(
    index,
    title="Customer Data App",
    description="A simple app to manage customer data.",
)

app.add_page(
    employee_view,
    title="Employee Page",
    description="Employee dashboard where he track his request.",
    route="/employee"
)

app.add_page(
    assignments_table,
    title="Blueprint Assignments",
    description="Page showing all blueprint assignment statuses.",
    route="/blueprint-assignments"
),