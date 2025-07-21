import reflex as rx
from buildcheck.components.status_tag import status_tag
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client


class ValidationState(UserState):
    violations: list[str] = []
    guidelines: list[dict] = []
    case_id: int = 0 
    @rx.event
    def load_report(self):
        # Loads the case data for the current user from the database
        try:
            user_id_int = int(str(self.user_id))
            response1 = supabase_client.table("cases").select("*").eq("submitter_id", user_id_int).single().execute()
            self.case_id = response1.data["id"]
            response2 = supabase_client.table("violations").select("*").eq("case_id", self.case_id).execute()
            self.violations = [row["guideline_code"] for row in response2.data]
            response3 = supabase_client.table("guidelines").select("*").execute() 
            self.guidelines = response3.data
        except Exception as e:
            print("Exception in load_caseData:", e)
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
    return rx.container(
            rx.script(src="https://unpkg.com/html2canvas-pro@1.5.11/dist/html2canvas-pro.js"),
            rx.script(src='./export-lib.js'),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon(tag="triangle_alert", color="orange", size=20),
                        rx.vstack(
                            rx.text("Partial Compliance", font_size="lg", font_weight="bold"),
                            rx.text(
                                "Your plans meet most requirements but need some adjustments.",
                                font_size="sm",
                                color="gray"
                            ),
                            spacing="1"
                        ),
                        spacing="4",
                        align_items="start"
                    ),
                    rx.hstack(
                        rx.box(
                            rx.text(f"{ValidationState.compliance_score * 100:.0f}%",
                                    font_weight="bold",
                                    style={"fontSize": "2rem"},
                                    color="green"),
                            rx.text("Compliance Score", font_size="sm", color="gray"),
                            text_align="center"
                        ),
                        rx.box(
                            rx.text(f"{ValidationState.guidelines.length() - ValidationState.violations.length() }",
                                    font_weight="bold",
                                    style={"fontSize": "2rem"},
                                    color="blue"),
                            rx.text("Passed Checks", font_size="sm", color="gray"),
                            text_align="center"
                        ),
                        rx.box(
                            rx.text(f"{ValidationState.violations.length() }",
                                    font_weight="bold",
                                    style={"fontSize": "2rem"},
                                    color="red"),
                            rx.text("Violations", font_size="sm", color="gray"),
                            text_align="center"
                        ),
                        spacing="4",
                        justify="center",
                        width="100%",
                        margin_top="3px",
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
            ),

            # Updated Compliance Table with label, borders
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Category"),
                        rx.table.column_header_cell("Title"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Details"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        ValidationState.guidelines,
                        lambda item: rx.table.row(
                            rx.table.cell(item["category"]),
                            rx.table.cell(item["title"]),
                            rx.table.cell(guideline_status(item["code"])),
                            rx.table.cell(item["description"]),
                        )
                    )
                ),
                striped=True,
                highlight_on_hover=True,
                with_border=True,
                variant="surface",
                size="3",
                width="100%"
            ),

            rx.button(
                "Download Report",
                color_scheme="blue",
                margin_top="10px",
                on_click=rx.call_script("downloadPDF()", callback=ValidationState.no_op)
            ),
        on_mount=ValidationState.load_report
        )