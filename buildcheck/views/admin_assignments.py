import reflex as rx
import reflex_enterprise as rxe

from .navbar import navbar

# Dummy data
assignments = [
    {"id": "BP001", "employee": "John Doe", "date": "2024-03-15", "status": "Unassigned", "reviewer": "Not Assigned"},
    {"id": "BP002", "employee": "Jane Smith", "date": "2024-03-16", "status": "In Review", "reviewer": "Alice Smith"},
    {"id": "BP003", "employee": "Peter Jones", "date": "2024-03-17", "status": "Completed", "reviewer": "Bob Johnson"},
    {"id": "BP004", "employee": "Mary Lee", "date": "2024-03-18", "status": "Completed", "reviewer": "Charlie Brown"},
    {"id": "BP005", "employee": "David Kim", "date": "2024-03-19", "status": "Unassigned", "reviewer": "Not Assigned"},
    {"id": "BP006", "employee": "Sarah Chen", "date": "2024-03-20", "status": "Unassigned", "reviewer": "Not Assigned"},
]

# ---------- STATE ----------

class AssignmentState(rx.State):
    search: str = ""
    selected_status: str = "All Statuses"

    def reset_filters(self):
        self.search = ""
        self.selected_status = "All Statuses"


    @rx.var   #This is a computed state variable
    def filtered_assignments(self) -> list[dict]:
        filtered = assignments.copy()  # Start with a copy of all assignments

        # Filter by status if needed
        if self.selected_status != "All Statuses":
            filtered = list(filter(lambda a: a["status"] == self.selected_status, filtered))

        # Filter by search query if needed
        if self.search.strip():
            query = self.search.strip().lower()
            filtered = list(filter(
                lambda a: query in a["employee"].lower() or query in a["id"].lower(),
                filtered
            ))

        return filtered
    

# ---------- COMPONENT HELPERS ----------

def status_tag(status: str) -> rx.Component:
    color_map = {
        "Unassigned": ("orange", "#fff7ed"),
        "In Review": ("blue", "#eff6ff"),
        "Completed": ("green", "#dcfce7"),
    }
    text_color, bg_color = color_map.get(status, ("#374151", "#f4f4f5"))  # fallback gray

    return rx.box(
        rx.text(status,
                color=text_color,
                font_size="sm",
                font_weight="medium"),

        bg=bg_color,
        padding_x="3",
        padding_y="1",
        border_radius="xl",
        # display="inline-block",
        border=f"0.5px solid {text_color}",
        border_color="lightgray",
        width="fit-content",
    )

def action_button(status: str, id_: str) -> rx.Component:
    return rx.button(
        rx.cond(status == "Unassigned", "Assign", "Reassign"),
        size="2",
        variant="outline",
        font_size="sm",
        on_click=rx.redirect(f"/assign/{id_}"),
    )


# ---------- MAIN TABLE COMPONENT ----------

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
                            AssignmentState.filtered_assignments,
                            lambda item: rx.table.row(
                                rx.table.cell(
                                    rx.text(item["id"], font_size="sm")
                                ),
                                rx.table.cell(
                                    rx.text(item["employee"], font_size="sm")
                                ),
                                rx.table.cell(
                                    rx.text(item["date"], font_size="sm")
                                ),
                                rx.table.cell(
                                    rx.link("View", href=f"/details/{item['id']}", color="blue", font_size="sm", font_weight="medium")
                                ),
                                rx.table.cell(status_tag(item["status"])),
                                rx.table.cell(
                                    rx.text(item["reviewer"], font_size="sm")
                                ),
                                rx.table.cell(
                                    rx.box(action_button(item["status"], item["id"]))
                                ),
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
