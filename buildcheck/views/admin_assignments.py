import reflex as rx
from typing import TypedDict

# Components
from buildcheck.components.navbar import navbar
from buildcheck.components.admin_status_tag import get_admin_status_tag
from buildcheck.components.footer import footer

# State imports
from buildcheck.views.assign_page import AssignmentState
from buildcheck.state.user_state import UserState


class Assignment(TypedDict):  # Represents a blueprint assignment
    id: str
    employee: str
    date: str
    status: str
    reviewer: str

def assign_dialog() -> rx.Component:
    return rx.dialog.content(
        rx.dialog.title("Assign Reviewer"),
        rx.dialog.description("Select a reviewer to assign to this blueprint."),
        rx.select(
            items=AssignmentState.reviewer_options,
            value=AssignmentState.selected_reviewer,
            on_change=AssignmentState.set_selected_reviewer,
            placeholder="Choose a reviewer",
            width="100%",
        ),
        rx.hstack(
            rx.dialog.close(
                rx.button("Cancel", variant="ghost")
            ),
            rx.button(
                "Submit",
                on_click=AssignmentState.reassign_selected_case,
                color_scheme="blue",
                is_disabled=AssignmentState.selected_reviewer == "",
            ),
            justify="end",
            spacing="4",
        ),
        bg="white",
        padding="4",
        border_radius="lg",
        box_shadow="lg",
        width="400px",
    )


def action_button(status: str, id_: str) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.cond(status == "Unassigned", "Assign", "Reassign"),
                size="2",
                variant="outline",
                font_size="sm",
                on_click=AssignmentState.set_selected_case(id_),
            )
        ),
        assign_dialog()
    )


def render_status(status: str) -> rx.Component:
    """Render a status badge based on the assignment status."""
    if status == "Unassigned":
        return rx.badge("Unassigned", color_scheme="gray", variant="soft")
    elif status == "In Review":
        return rx.badge("In Review", color_scheme="blue", variant="soft")
    return rx.badge("Completed", color_scheme="green", variant="soft")


def assignment_row(item: Assignment) -> rx.Component:
    """Create a table row for an assignment."""
    return rx.table.row(
        rx.table.cell(rx.text(item["id"], font_size="sm")),
        rx.table.cell(rx.text(item["employee"], font_size="sm")),
        rx.table.cell(rx.text(item["date"], font_size="sm")),
        rx.table.cell(
            rx.link(
                "View",
                href=f"/details/{item['id']}",
                color="blue",
                font_size="sm",
                font_weight="medium",
            )
        ),
        rx.table.cell(get_admin_status_tag(item["status"])),
        rx.table.cell(rx.text(item["reviewer"], font_size="sm")),
        rx.table.cell(rx.box(action_button(item["status"], item["id"]))),
    )


def assignments_table() -> rx.Component:
    return navbar(), rx.container(
        rx.vstack(
            rx.heading("Blueprint Assignments", size="5", margin_top="1em"),
            rx.spacer(),
            rx.text(lambda: f"Current User: {UserState.name} ({UserState.role})", font_size="sm", color="gray"),
            rx.hstack(
                rx.input(
                    placeholder="Search by ID or Employee...",
                    value=AssignmentState.search,
                    on_change=AssignmentState.set_search,
                    width="40%",
                    size="2",
                ),
                rx.select(
                    items=["All Statuses", "Unassigned", "In Review", "Completed"],
                    value=AssignmentState.selected_status,
                    on_change=AssignmentState.set_selected_status,
                    width="20%",
                    size="2",
                ),
                rx.button("Clear Filters", on_click=AssignmentState.reset_filters, size="2"),

                spacing="4",
                margin_y="1",
                width="100%",
            ),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ID"),
                            rx.table.column_header_cell("Employee"),
                            rx.table.column_header_cell("Date"),
                            rx.table.column_header_cell("Details"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Reviewer"),
                            rx.table.column_header_cell("Actions"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AssignmentState.filtered_assignments.to(list[Assignment]),
                            assignment_row,
                        )
                    ),
                    striped=True,
                    highlight_on_hover=True,
                    width="100%",
                ),
                width="100%",
            ),
           
            rx.hstack(
                rx.text("Showing filtered results", font_size="sm", color="gray"),
                justify="end",
                width="100%",
                margin_top="1",
            ),
            spacing="4",
            padding="4",
            width="100%",
        ),
        spacing="4",
        padding="4",
        width="100%",
    ), footer()


@rx.page(route="/admin-assignments", on_load=AssignmentState.load_assignments)
def admin_assignments() -> rx.Component:
    return assignments_table()
