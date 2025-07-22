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


def action_button(status: str, id_: str) -> rx.Component:
    """Return an Assign/Reassign button based on status."""
    return rx.button(
        rx.cond(status == "Unassigned", "Assign", "Reassign"),
        size="2",
        variant="outline",
        font_size="sm",
        on_click=[
            AssignmentState.set_selected_case(id_),
            AssignmentState.open_modal(),
        ],
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
            rx.text(f"Current User: {UserState.name} ({UserState.role})", font_size="sm", color="gray"),
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
                rx.button(
                    "Assign New Blueprint",
                    color_scheme="blue",
                    size="2",
                    on_click=AssignmentState.open_new_assign_modal(),
                ),
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
            # Modal for reassigning
            rx.cond(
                AssignmentState.is_modal_open,
                rx.box(
                    rx.box(
                        position="fixed",
                        top=0,
                        left=0,
                        width="100vw",
                        height="100vh",
                        bg="rgba(0,0,0,0.4)",
                        z_index=1000,
                    ),
                    rx.center(
                        rx.card(
                            rx.vstack(
                                rx.heading(
                                    rx.cond(
                                        AssignmentState.selected_case_id == "",
                                        "Assign Reviewer",
                                        "Reassign Reviewer",
                                    ),
                                    size="4"
                                ),
                                rx.text("Select Reviewer:"),
                                rx.select(
                                    items=AssignmentState.reviewer_options,
                                    value=AssignmentState.selected_reviewer,
                                    on_change=AssignmentState.set_selected_reviewer,
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.button("Cancel", on_click=AssignmentState.close_modal, variant="ghost"),
                                    rx.button(
                                        "OK",
                                        color_scheme="blue",
                                        on_click=AssignmentState.reassign_selected_case,
                                        is_disabled=AssignmentState.selected_reviewer == "",
                                    ),
                                ),
                                spacing="4",
                            ),
                            width="350px",
                            padding="2em",
                            box_shadow="lg",
                            bg="white",
                            z_index=1001,
                        ),
                        position="fixed",
                        top="50%",
                        left="50%",
                        transform="translate(-50%, -50%)",
                        z_index=1001,
                    ),
                ),
                None,
            ),
            # Modal for assigning new blueprint
            rx.cond(
                AssignmentState.is_new_assign_modal_open,
                rx.box(
                    rx.box(
                        position="fixed",
                        top=0,
                        left=0,
                        width="100vw",
                        height="100vh",
                        bg="rgba(0,0,0,0.4)",
                        z_index=1000,
                    ),
                    rx.center(
                        rx.card(
                            rx.vstack(
                                rx.heading("Assign New Blueprint", size="4"),
                                rx.text("Select Blueprint:"),
                                rx.select(
                                    items=AssignmentState.unassigned_blueprints,
                                    value=AssignmentState.selected_new_blueprint,
                                    on_change=AssignmentState.set_selected_new_blueprint,
                                    width="100%",
                                ),
                                rx.text("Select Reviewer:"),
                                rx.select(
                                    items=AssignmentState.reviewer_options,
                                    value=AssignmentState.selected_new_reviewer,
                                    on_change=AssignmentState.set_selected_new_reviewer,
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.button("Cancel", on_click=AssignmentState.close_new_assign_modal, variant="ghost"),
                                    rx.button(
                                        "Assign",
                                        color_scheme="blue",
                                        on_click=AssignmentState.assign_new_blueprint,
                                        is_disabled=(
                                            AssignmentState.selected_new_blueprint == ""
                                            or AssignmentState.selected_new_reviewer == ""
                                        ),
                                    ),
                                ),
                                spacing="4",
                            ),
                            width="350px",
                            padding="2em",
                            box_shadow="lg",
                            bg="white",
                            z_index=1001,
                        ),
                        position="fixed",
                        top="50%",
                        left="50%",
                        transform="translate(-50%, -50%)",
                        z_index=1001,
                    ),
                ),
                None,
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
