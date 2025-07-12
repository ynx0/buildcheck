import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from typing import List

data: List[dict] = [
    {"id": "444", "submitter": "Brian Hall", "date": "2025-6-4", "status": "pending"},
    {"id": "411", "submitter": "John Robinson", "date": "2025-5-24", "status": "pending"},
    {"id": "405", "submitter": "David Lee", "date": "2024-9-14", "status": "pending"},
    {"id": "403", "submitter": "Christopher Clark", "date": "2024-8-29", "status": "rejected"},
]


class ReviewerAssignmentState(rx.State):
    bp_total: int = 20
    bp_approved: int = 8



def blueprint_table() -> rx.Component:
    # TODO reuse code from employee view
    def table_row(assigned) -> rx.Component:
        return rx.table.row(
            rx.table.cell(assigned["id"], justify="center"),
            rx.table.cell(assigned["submitter"], justify="center"),
            rx.table.cell(assigned["date"], justify="center"),
            rx.table.cell(status_tag(assigned["status"]), justify="center"),
            rx.table.cell(rx.link("view", href="#"), justify="center"),
        )

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Blueprint ID", justify="center"),
                rx.table.column_header_cell("Submitter", justify="center"),
                rx.table.column_header_cell("Date", justify="center"),
                rx.table.column_header_cell("Status", justify="center"),
                rx.table.column_header_cell("Actions", justify="center"),
            )
        ),
        rx.table.body(
            *(table_row(assigned) for assigned in data)
        ),
        width="100%",
        max_width="40em",
        overflow_x="auto",
        padding="1em",
        variant="surface"
    )


def blueprints_card() -> rx.Component:
    return rx.flex(
        rx.card(
            rx.vstack(
                rx.text("Total Blueprints"),
                rx.heading(ReviewerAssignmentState.bp_total, size="6"),
                align="center"
            ),
        ),
        rx.card(
            rx.vstack(
                rx.text("Approved Blueprints"),
                rx.heading(ReviewerAssignmentState.bp_approved, size="6"),
                align="center",
            ),
            size="1",
        ),
        spacing="2",
        align_items="flex-start",
        flex_wrap="wrap",
    )



def search() -> rx.Component:
    return rx.hstack(
        rx.input(
            rx.input.slot(rx.icon("search")),
            placeholder="Search...",
            max_width="225px",
            width="100%",
            variant="surface",
        ),
        rx.select(["id", "submitter", "date", "status"], placeholder="Sort By: ID", width="20%"),
        rx.input(type="date"),
        spacing="4",
    )

@rx.page(route='/assignments')
def rv_assignment() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading("Assigned Blueprints", size="9"),
        blueprints_card(),
        search(),
        blueprint_table(),
        footer(),
        spacing="3",
        padding="3",
        padding_x=["1.5em", "1.5em", "3em"]
    )
