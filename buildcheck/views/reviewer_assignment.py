import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.backend.supabase_client import supabase_client
from buildcheck.state.user_state import UserState
from typing import List


data: List[dict] = [
    {"id": "444", "submitter": "Noura Alnaimi", "date": "2025-7-16", "status": "pending"},
    {"id": "411", "submitter": "John Robinson", "date": "2025-5-24", "status": "pending"},
    {"id": "405", "submitter": "David Lee", "date": "2024-9-14", "status": "pending"},
    {"id": "403", "submitter": "Christopher Clark", "date": "2024-8-29", "status": "rejected"},
]

class ReviewerAssignmentState(rx.State):
    assignments: List[dict] = []
    bp_total: int = 0
    bp_approved: int = 0

    @rx.event
    async def load_assignments(self):
        try:
            user_state = await self.get_state(UserState)
            reviewer_id = int(user_state.user_id)

            response = supabase_client.table("cases").select(
                "id, submitted_at, status, blueprint_path, users!cases_submitter_id_fkey(name)"
            ).eq("reviewer_id", reviewer_id).order("submitted_at", desc=True).execute()

            case_data = response.data or []

            self.assignments = [
                {
                    "id": c["id"],
                    "submitter": c.get("users", {}).get("name", "Unknown"),
                    "date": c["submitted_at"].split("T")[0],
                    "status": c["status"].capitalize(),
                    "path": c["blueprint_path"]
                }
                for c in case_data
            ]

            self.bp_total = len(self.assignments)
            self.bp_approved = sum(1 for c in self.assignments if c["status"].lower() == "approved")

        except Exception as e:
            print(f"[load_assignments ERROR] {e}")
            self.assignments = []
            self.bp_total = 0
            self.bp_approved = 0



def blueprint_table() -> rx.Component:
    def table_row(assigned) -> rx.Component:
        return rx.table.row(
            rx.table.cell(assigned["id"], justify="center"),
            rx.table.cell(assigned["submitter"], justify="center"),
            rx.table.cell(assigned["date"], justify="center"),
            rx.table.cell(status_tag(assigned["status"]), justify="center"),
            rx.table.cell(rx.link("View", href="/blueprint-pending"), justify="center"),
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
            rx.cond(
                ReviewerAssignmentState.assignments,
                rx.foreach(
                    ReviewerAssignmentState.assignments,
                    lambda assigned: table_row(assigned)
                ),
                rx.table.row(
                    rx.table.cell("No assignments found", col_span=5, justify="center")
                )
            )
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


@rx.page(route='/assignments', on_load=ReviewerAssignmentState.load_assignments)
def rv_assignment() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading("Assigned Blueprints", size="9"),
        blueprints_card(),
        search(),
        blueprint_table(),
        spacing="3",
        padding="3",
        padding_x=["1.5em", "1.5em", "3em"]
    ), footer()
