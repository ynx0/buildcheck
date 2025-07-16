import reflex as rx
from typing import TypedDict
from buildcheck.components.navbar import navbar
from buildcheck.components.admin_status_tag import get_admin_status_tag


class Assignment(TypedDict):
    id: str
    employee: str
    date: str
    status: str
    reviewer: str


assignments: list[Assignment] = [
    {"id": "BP001", "employee": "John Doe", "date": "2024-03-15", "status": "Unassigned", "reviewer": "Not Assigned"},
    {"id": "BP002", "employee": "Jane Smith", "date": "2024-03-16", "status": "In Review", "reviewer": "Alice Smith"},
    {"id": "BP003", "employee": "Peter Jones", "date": "2024-03-17", "status": "Completed", "reviewer": "Bob Johnson"},
    {"id": "BP004", "employee": "Mary Lee", "date": "2024-03-18", "status": "Completed", "reviewer": "Charlie Brown"},
    {"id": "BP005", "employee": "David Kim", "date": "2024-03-19", "status": "Unassigned", "reviewer": "Not Assigned"},
    {"id": "BP006", "employee": "Sarah Chen", "date": "2024-03-20", "status": "Unassigned", "reviewer": "Not Assigned"},
]


class AssignmentState(rx.State):
    search: str = ""
    selected_status: str = "All Statuses"

    def reset_filters(self):
        self.search = ""
        self.selected_status = "All Statuses"

    @rx.var
    def filtered_assignments(self) -> list[Assignment]:
        filtered = assignments.copy()

        if self.selected_status != "All Statuses":
            filtered = list(filter(lambda a: a["status"] == self.selected_status, filtered))

        if self.search.strip():
            query = self.search.strip().lower()
            filtered = list(filter(
                lambda a: query in a["employee"].lower() or query in a["id"].lower(),
                filtered
            ))

        return filtered


def action_button(status: str, id_: str) -> rx.Component:
    return rx.button(
        rx.cond(status == "Unassigned", "Assign", "Reassign"),
        size="2",
        variant="outline",
        font_size="sm",
        on_click=rx.redirect(f"/assign/{id_}"),
    )

def render_status(status) -> rx.Component:
    return rx.cond(
        status == "Unassigned",
        rx.badge("Unassigned", color_scheme="gray", variant="soft"),
        rx.cond(
            status == "In Review",
            rx.badge("In Review", color_scheme="blue", variant="soft"),
            rx.badge("Completed", color_scheme="green", variant="soft")
        )
    )


def assignments_table() -> rx.Component:
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("Blueprint Assignments", size="5", margin_top="1em"),
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
                rx.button("Assign New Blueprint", color_scheme="blue", size="2", on_click=rx.redirect("/new")),
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
                            lambda item: rx.table.row(
                                rx.table.cell(rx.text(item["id"], font_size="sm")),
                                rx.table.cell(rx.text(item["employee"], font_size="sm")),
                                rx.table.cell(rx.text(item["date"], font_size="sm")),
                                rx.table.cell(
                                    rx.link("View", href=f"/details/{item['id']}", color="blue", font_size="sm", font_weight="medium")
                                ),
                                rx.table.cell(get_admin_status_tag(item["status"])),
                                rx.table.cell(rx.text(item["reviewer"], font_size="sm")),
                                rx.table.cell(rx.box(action_button(item["status"], item["id"]))),
                            )
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
        ),
        spacing="4",
        padding="4",
        width="100%",
    )


@rx.page(route="/admin_assignments")
def admin_assignments() -> rx.Component:
    return assignments_table()
