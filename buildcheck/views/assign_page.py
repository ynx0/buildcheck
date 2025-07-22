
import reflex as rx
from buildcheck.backend.supabase_client import supabase_client
from buildcheck.state.user_state import UserState


# This page to mange blueprint assignments and reviewer selection

class AssignmentState(rx.State):
    # Modal state for assigning new blueprint
    is_new_assign_modal_open: bool = False
    unassigned_blueprints: list[str] = []
    selected_new_blueprint: str = ""
    selected_new_reviewer: str = ""
    @rx.event

    def open_new_assign_modal(self):
        # Fetch unassigned blueprints from DB (reviewer_id IS NULL)
        cases = supabase_client.table("cases").select("id").is_("reviewer_id", None).execute().data
        self.unassigned_blueprints = [f"BP{c['id']:03}" for c in cases] if cases else []
        # Fetch reviewers if not already loaded
        if not self.reviewer_options:
            reviewers = supabase_client.table("users").select("id, name").eq("role", "reviewer").execute().data
            self.reviewer_options = [f"{r['id']} - {r['name']}" for r in reviewers]
        self.selected_new_blueprint = ""
        self.selected_new_reviewer = ""
        self.is_new_assign_modal_open = True

    @rx.event
    def close_new_assign_modal(self):
        self.is_new_assign_modal_open = False
        self.selected_new_blueprint = ""
        self.selected_new_reviewer = ""

    @rx.event
    def set_selected_new_blueprint(self, blueprint: str):
        self.selected_new_blueprint = blueprint

    @rx.event
    def set_selected_new_reviewer(self, reviewer: str):
        self.selected_new_reviewer = reviewer

    @rx.event
    def assign_new_blueprint(self):
        if not self.selected_new_blueprint or not self.selected_new_reviewer:
            yield rx.toast.error("Please select both a blueprint and a reviewer.")
            return
        reviewer_id = self.selected_new_reviewer.split(" - ")[0]
        try:
            digits = "".join(filter(str.isdigit, self.selected_new_blueprint))
            if not digits:
                raise ValueError("No digits found in blueprint id")
            case_number = int(digits)
        except ValueError:
            yield rx.toast.error("Invalid blueprint ID.")
            return
        supabase_client.table("cases").update({
            "reviewer_id": int(reviewer_id),
            "status": "pending"
        }).eq("id", case_number).execute()
        yield rx.toast.success(f"Reviewer assigned to Blueprint {self.selected_new_blueprint}")
        self.is_new_assign_modal_open = False
        self.selected_new_blueprint = ""
        self.selected_new_reviewer = ""
        # Reload assignments
        yield AssignmentState.load_assignments()
    # Modal state for in-page assign/reassign
    is_modal_open: bool = False
    selected_reviewer: str = ""
    
    @rx.event
    def open_modal(self):
        self.is_modal_open = True
        self.selected_reviewer = ""

    @rx.event
    def close_modal(self):
        self.is_modal_open = False
        self.selected_reviewer = ""

    @rx.event
    def set_selected_reviewer(self, reviewer: str):
        self.selected_reviewer = reviewer

    @rx.event
    def reassign_selected_case(self):
        # Use selected_case_id and selected_reviewer to update the assignment
        if not self.selected_case_id or not self.selected_reviewer:
            yield rx.toast.error("Please select a reviewer.")
            return
        reviewer_id = self.selected_reviewer.split(" - ")[0]
        try:
            digits = "".join(filter(str.isdigit, self.selected_case_id))
            if not digits:
                raise ValueError("No digits found in case_id")
            case_number = int(digits)
        except ValueError:
            yield rx.toast.error("Invalid blueprint ID.")
            return
        supabase_client.table("cases").update({
            "reviewer_id": int(reviewer_id),
            "status": "pending"
        }).eq("id", case_number).execute()
        yield rx.toast.success(f"Reviewer assigned to Blueprint {self.selected_case_id}")
        self.is_modal_open = False
        self.selected_reviewer = ""
        # Optionally reload assignments
        yield AssignmentState.load_assignments()

    @rx.var
    def filtered_assignments(self) -> list[dict]: #this is to filter assignments based on search and status
        filtered = self.assignments
        # Filter by status if not 'All Statuses'
        if self.selected_status and self.selected_status != "All Statuses":
            filtered = [a for a in filtered if a["status"] == self.selected_status]
        # Filter by search string in id or employee
        if self.search:
            s = self.search.lower()
            filtered = [a for a in filtered if s in a["id"].lower() or s in a["employee"].lower()]
        return filtered
    selected_case_id: str = ""
    current_reviewer_name: str = ""
    reviewer_options: list[str] = []
    search: str = ""
    selected_status: str = "All Statuses"
    assignments: list[dict] = []

    @rx.event
    def reset_filters(self): # Reset search and status filters to default.
        self.search = ""
        self.selected_status = "All Statuses"

    @rx.var
    def selected_case_number(self) -> int: # Extract the numeric part of the selected_case_id as an integer.
        digits = "".join(filter(str.isdigit, self.selected_case_id))
        return int(digits) if digits else -1

    @rx.event
    def set_selected_case(self, case_id: str):#set the selected case and update reviewer info/options.
        self.selected_case_id = case_id

        # Extract case number from case_id
        try:
            case_number = int("".join(filter(str.isdigit, case_id)))
        except ValueError:
            self.current_reviewer_name = "Invalid Blueprint ID"
            return

        # Fetch reviewer options
        reviewers = supabase_client.table("users").select("id, name").eq("role", "reviewer").execute().data
        self.reviewer_options = [f"{r['id']} - {r['name']}" for r in reviewers]

        # Fetch current reviewer for the case
        case_data = supabase_client.table("cases").select("reviewer_id").eq("id", case_number).single().execute().data
        reviewer_id = case_data.get("reviewer_id") if case_data else None
        if not reviewer_id:
            self.current_reviewer_name = "Not Assigned"
        else:
            reviewer_info = supabase_client.table("users").select("name").eq("id", reviewer_id).single().execute().data
            self.current_reviewer_name = reviewer_info["name"] if reviewer_info else "Unknown"

    @rx.event
    async def load_assignments(self): #load all assignments and map user IDs to names.
        response = supabase_client.table("cases").select("id, submitted_at, status, submitter_id, reviewer_id").execute()
        users = supabase_client.table("users").select("id, name").execute()
        user_map = {str(user["id"]): user["name"] for user in users.data}

        self.assignments = [
            {
                "id": f"BP{case['id']:03}",
                "employee": user_map.get(str(case["submitter_id"]), "Unknown"),
                "date": case["submitted_at"].split("T")[0],
                "status": case["status"],
                "reviewer": user_map.get(str(case["reviewer_id"]), "Not Assigned"),
                # Example: add a flag if this assignment belongs to the current user
                "is_current_user": str(case["submitter_id"]) == UserState.user_id,
            }
            for case in response.data
        ]

    @rx.event
    async def assign_case(self, case_id: str, form_data: dict): #assign a reviewer to a blueprint case.
        reviewer_id_raw = form_data.get("reviewer_id", "")
        if not reviewer_id_raw:
            yield rx.toast.error("Please select a reviewer.")
            return

        reviewer_id = reviewer_id_raw.split(" - ")[0]
        # Extract case number from case_id
        try:
            digits = "".join(filter(str.isdigit, case_id))
            if not digits:
                raise ValueError("No digits found in case_id")
            case_number = int(digits)
        except ValueError:
            yield rx.toast.error("Invalid blueprint ID.")
            return

        # Update the case with the new reviewer
        supabase_client.table("cases").update({
            "reviewer_id": int(reviewer_id),
            "status": "pending"
        }).eq("id", case_number).execute()

        yield rx.toast.success(f"Reviewer assigned to Blueprint {case_id}")
        yield rx.redirect("/admin-assignments")


@rx.page(route="/assign")
def assign_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading(f"Reassign Reviewer for {AssignmentState.selected_case_id}", size="4"),
            rx.text(f"Current Reviewer: {AssignmentState.current_reviewer_name}", color="gray"),
            rx.form(
                rx.select(
                    AssignmentState.reviewer_options,
                    name="reviewer_id",
                    placeholder="Select Reviewer",
                    width="100%",
                ),
                rx.button("Reassign", type_="submit", color_scheme="blue"),
                on_submit=lambda data: AssignmentState.assign_case(AssignmentState.selected_case_id, data),
                width="100%",
            ),
            rx.button("Back", on_click=rx.redirect("/admin-assignments"), variant="ghost"),
            spacing="4",
            width="400px",
            margin_top="2em",
        ),
        align="center",
        justify="center",
        min_height="60vh",
    )