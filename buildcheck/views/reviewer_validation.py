import reflex as rx
from buildcheck.components.stat_card import stat_card
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client

class AIValidationState(UserState):
    violations: list[str] = []
    guidelines: list[dict] = []
    case_data: list[dict] = []
    case_result: str = "No cases assigned"  # Default case result status
    case_id: str = ""
    listOfCases: list[str] = []
    comments: dict = {}

    @rx.event
    def load_data(self):
        # Loads the case data for the current user from the database
        try:
            user_id_int = int(self.user_id)
            response1 = supabase_client.table("cases").select("*").eq("reviewer_id", user_id_int).execute()
            self.case_id = str(response1.data[0]["id"])
            self.case_data = response1.data
            self.listOfCases = [str(case["id"]) for case in self.case_data]
            response2 = supabase_client.table("violations").select("guideline_code").eq("case_id", self.case_id).execute()
            self.violations = [row["guideline_code"] for row in response2.data]
            response3 = supabase_client.table("guidelines").select("*").execute() 
            self.guidelines = response3.data
        except Exception as e:
            print("Exception in load_data:", e)

    @rx.event
    def change_case(self, value: str):
        self.case_id = value

    @rx.event
    def handle_comments(self, form_data: dict):
        # Store the comment locally
        self.comments = form_data
        # Update the comments column in the cases table for the selected case_id
        try:
            comment_text = form_data.get("comment", "")
            supabase_client.table("cases").update({"comments": comment_text}).eq("id", self.case_id).execute()
        except Exception as e:
            print("Exception in handle_comments:", e)

    @rx.event
    def no_op(self):
        pass

    @rx.var
    def compliance_score(self) -> float:
        if len(self.guidelines) == 0:
            return 0.0
        return (len(self.guidelines)- len(self.violations)) / len(self.guidelines)
    

def guideline_status(guideline: str) -> rx.Component:
    return rx.cond(AIValidationState.violations.contains(guideline), status_tag("rejected"), status_tag("approved")) 
    
def validation_page() -> rx.Component:
    return rx.vstack(
            navbar(),
            rx.hstack(
                rx.text("Blueprint ID:", font_weight="bold"),
                rx.select(
                    AIValidationState.listOfCases,
                    value=AIValidationState.case_id,
                    on_change=AIValidationState.change_case,
                    width="200px"
                ),
                rx.button(
                    "Approve",
                    color_scheme="blue",
                    on_click=lambda: [
                        rx.toast.success("Blueprint approved!"),
                        rx.redirect("/assignments")
                    ]
                ),
                rx.button(
                    "Reject",
                    color_scheme="red",
                    on_click=lambda: [rx.toast.error("Blueprint rejected!"), rx.redirect("/assignments")]
                ),
                margin="15px"
            ),
            rx.heading("AI Compliance Overview", size="6"),
            rx.hstack(
                stat_card("Overall Compliance", f"{AIValidationState.compliance_score * 100}%", "circle-check-big", "green", "Compliance across all building guidelines."),
                stat_card("Critical Violations", f"{AIValidationState.violations.length()}", "circle-x", "#d62828", "High-priority issues requiring immediate attention."),
                stat_card("Pending Reviews", f"{AIValidationState.listOfCases.length()}", "hourglass", "#220bb4", "BlueprintsSections awaiting manual verification or dispute resolution."),
            margin_bottom="2em",
            ),
            rx.heading("Detailed Compliance Report", size="5"),
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.input(
                        rx.input.slot(
                            rx.icon(tag="search"),
                        ),
                        placeholder="Search compliance items...",
                        width="400px"
                        ),
                        rx.button(rx.icon(tag="list-filter"), "Status")
                    ),
                    rx.hstack(),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("Title"),
                                rx.table.column_header_cell("Rule Description"),
                                rx.table.column_header_cell("Status"),
                                rx.table.column_header_cell("Category"),
                                rx.table.column_header_cell("Actions"),
                            ) 
                        ),
                        rx.table.body(
                            rx.foreach(
                            AIValidationState.guidelines,
                            lambda item: rx.table.row(
                                rx.table.cell(item["code"]),
                                rx.table.cell(item["title"]),
                                rx.table.cell(item["description"]),
                                rx.table.cell(guideline_status(item["code"])),
                                rx.table.cell(item["category"]),
                                rx.table.cell(rx.button("Delete", color_scheme="red"))
                            )
                            )
                        ),
                    ),
                    rx.heading("Add Comments", size="4"),
                    rx.form.root(
                    rx.hstack(
                        rx.input(
                            name="input",
                            placeholder="Enter text...",
                            type="text",
                            required=True,
                            size="3",
                            width="70%",
                        ),
                        rx.button("Add", type="submit"),
                        width="100%",
                    ),
                    on_submit=AIValidationState.handle_comments,
                    reset_on_submit=True,
                    ),
                ),
            ),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
            on_mount=AIValidationState.load_data
        ), footer()
