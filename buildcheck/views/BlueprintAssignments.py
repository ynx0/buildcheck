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

class AssignmentState(rx.State):
    search: str = ""
    selected_status: str = "All Statuses"

    def reset_filters(self):
        self.search = ""
        self.selected_status = "All Statuses"

    @rx.var
    def filtered_assignments(self) -> list[dict]:
        filtered = assignments
        if self.selected_status != "All Statuses":
            filtered = [a for a in filtered if a["status"] == self.selected_status]
        if self.search.strip():
            query = self.search.strip().lower()
            filtered = [
                a for a in filtered
                if query in a["employee"].lower() or query in a["id"].lower()
            ]
        return [
            {
                "ID": item["id"],
                "Employee": item["employee"],
                "Date": item["date"],
                "Details": rx.link("View", href=f"/details/{item['id']}", color="blue"),
                "Status": status_tag(item["status"]),
                "Reviewer": item["reviewer"],
                "Action": action_button(item["status"]),
            }
            for item in filtered
        ]

def status_tag(status: str) -> rx.Component:
    color_map = {
        "Unassigned": ("orange", "#fff7ed"),
        "In Review": ("blue", "#eff6ff"),
        "Completed": ("green", "#dcfce7"),
    }
    text_color, bg_color = color_map.get(status, ("gray", "#f4f4f5"))
    return rx.box(
        rx.text(status, color=text_color, font_size="sm", font_weight="medium"),
        background_color=bg_color,
        padding_x="2",
        padding_y="0.5",
        border_radius="md",
        display="inline-block",
    )

def action_button(status: str) -> rx.Component:
    return rx.button(
        "Reassign" if status != "Unassigned" else "Assign",
        size="2",
        variant="outline",
        on_click=rx.redirect(f"/assign/{status.lower()}"),  # Example action
    )

def assignments_table() -> rx.Component:
    return rx.container(
        rx.vstack(
            navbar(),
            rx.heading("Blueprint Assignments", size="4", margin_top="1"),
            rx.hstack(
                rx.input(
                    placeholder="Search by ID or Employee...",
                    value=AssignmentState.search,
                    on_change=AssignmentState.set_search,
                    width="40%",
                ),
                rx.select(
                    items=["All Statuses", "Unassigned", "In Review", "Completed"],
                    value=AssignmentState.selected_status,
                    on_change=AssignmentState.set_selected_status,
                    width="20%",
                ),
                rx.button(
                    "Clear Filters",
                    on_click=AssignmentState.reset_filters,
                    variant="ghost",
                ),
                rx.button("Assign New Blueprint", color_scheme="blue", on_click=rx.redirect("/new")),
                spacing="4",
                margin_y="1",
                width="100%",
            ),
            rx.data_table(
                data=AssignmentState.filtered_assignments,
                columns=[
                    {"header": "ID", "accessor_key": "ID"},
                    {"header": "Employee", "accessor_key": "Employee"},
                    {"header": "Date", "accessor_key": "Date"},
                    {"header": "View Details", "accessor_key": "Details"},
                    {"header": "Status", "accessor_key": "Status"},
                    {"header": "Reviewer", "accessor_key": "Reviewer"},
                    {"header": "Actions", "accessor_key": "Action"},
                ],
                pagination=True,
                search=True,
                width="100%",
                striped=True,
                highlight_on_hover=True,
            ),
            rx.hstack(
                rx.text("Showing filtered results", font_size="sm", color="gray"),
                justify="end",
                width="100%",
                margin_top="1",
            ),
        ),
        padding="4",
        width="100%",
    )

