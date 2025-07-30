import reflex as rx
from buildcheck.components.status_tag import status_tag
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client
import traceback
from buildcheck.views.reviewer_validation import AIValidationState
from buildcheck.components.stat_card import stat_card

class ValidationState(rx.State):
    violations: list[str] = []
    guidelines: list[dict] = []
    case_id: int = 0 
    case_result: str = ""  # Default case result status
    @rx.event
    async def load_report(self):
        # Loads the case data for the current user from the database
        try:
            user_state = await self.get_state(UserState)
            response1 = supabase_client.table("cases").select("*").eq("submitter_id", user_state.user_id).single().execute()
            self.case_id = response1.data["id"]
            self.case_result = response1.data["status"]
            response2 = supabase_client.table("violations").select("*").eq("case_id", self.case_id).execute()
            self.violations = [row["guideline_code"] for row in response2.data]
            response3 = supabase_client.table("guidelines").select("*").execute() 
            self.guidelines = response3.data
        except Exception as e:
            print("Exception in load_caseData:", e)
            traceback.print_exc() 
    @rx.event
    def no_op(self):
        # needed to suppress _call_script no callback error
        pass
    @rx.var
    def compliance_score(self) -> float:
        if len(self.guidelines) == 0:
            return 0.0
        return (len(self.guidelines)- len(self.violations)) / len(self.guidelines)

def guideline_status(guideline: str) -> rx.Component:
    return rx.cond(ValidationState.violations.contains(guideline), status_tag("rejected"), status_tag("approved")) 


def compliance_card() -> rx.Component:
    return rx.container (
            rx.script(src="https://unpkg.com/html2canvas-pro@1.5.11/dist/html2canvas-pro.js"),
            rx.script(src='/export-lib.js'),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        stat_card("Overall Compliance", AIValidationState.compliance_score, "circle-check-big", "green", "Compliance across all building guidelines."),
                        stat_card("Critical Violations", AIValidationState.violations.length(), "circle-x", "#d62828", "High-priority issues requiring immediate attention."),
                        stat_card("Pending Reviews", AIValidationState.listOfCases.length(), "hourglass", "#220bb4", "BlueprintsSections awaiting manual verification or dispute resolution."),
                    margin_bottom="2em",
                    ),
                    rx.hstack(
                        rx.box(
                            rx.cond(
                                AIValidationState.visualization_path is not None,
                                rx.image(src=rx.get_upload_url(AIValidationState.visualization_path), width="100%", height="auto", object_fit="contain"),
                                rx.box(),  # Empty box to preserve space
                            ),
                            width="50%",  # or adjust as needed
                            height="100%",
                            bg="gray.50",  # optional placeholder background
                        ),
                            spacing="4",
                            background_color="#F0F4FF",
                            padding="4px",
                            margin_y="10px",
                            width="100%",
                            border_radius="8px"
                        ),
                        width="100%",
                        align_self="stretch",
                        margin_bottom="4px",
                        padding="4px",
                )
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Detailed Compliance Report", size="5"),
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
                    rx.cond(
                        ~AIValidationState.violated_guidelines,
                        rx.text('No violations to display.', font_weight="bold", size="5"),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("ID"),
                                    rx.table.column_header_cell("Title"),
                                    rx.table.column_header_cell("Rule Description"),
                                    # rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Category"),
                                    rx.table.column_header_cell("Actions"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AIValidationState.violated_guidelines,
                                    lambda item: rx.table.row(
                                        rx.table.cell(item["id"]),
                                        rx.table.cell(item["title"]),
                                        rx.table.cell(item["description"]),
                                        # rx.table.cell(guideline_status(item["id"])),
                                        rx.table.cell(item["category"]),
                                        # TODO this button should delete
                                        rx.table.cell(rx.button(
                                            "Delete",
                                            color_scheme="red",
                                            on_click=AIValidationState.on_violation_delete(item['id'])
                                        ))
                                    )
                                )
                            ),
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
                        reset_on_submit=True
                    ),
                )
            ),
            rx.button(
                "Download Report",
                color_scheme="blue",
                margin_top="10px",
                on_click=rx.call_script("downloadPDF()", callback=ValidationState.no_op)
            ),
            on_mount=ValidationState.load_report
        )