import reflex as rx
from buildcheck.components.status_tag import status_tag
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client
import traceback
from buildcheck.components.stat_card import stat_card
from buildcheck.backend.validation import run_validation
import asyncio
from typing import Optional
from buildcheck.backend.validation import Failure
from buildcheck.backend.blueprints import bp_name2vispath
from pathlib import Path
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client
import buildcheck.backend.email_utils as em
import traceback
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AIDecision(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"



class AIValidationState(rx.State):
    violations: list[int] = []
    guidelines: list[dict] = []
    case_data: list[dict] = []
    case_id: int
    listOfCases: list[str] = []
    comments: list[dict] = []  # Store comments from database
    is_validating: bool = False
    case_result: str = ""  # Default case result status
    vis_output_trigger: int


    def write_violations(self, failures: list[Failure]):
        print(f'{failures=}')
        failure_codes = list(map(lambda f: f.guideline.value, failures))

        # we need to overwrite all previous violations,
        # to prevent stale violations

        # unfortunately supabase-py does not support atomic transactions


        # delete all current violations for this case
        (supabase_client.table("violations")
            .delete()
            .eq("case_id", self.case_id)
            .execute()
        )


        # insert all the violations for current case
        if failure_codes:
            (supabase_client.table("violations")
                .insert([
                    {
                        "case_id": self.case_id,
                        "guideline_code": code
                    } for code in failure_codes
                ])
                .execute()
            )

        # update the cases ai_descision
        ai_decision = AIDecision.REJECTED.value if failures else AIDecision.APPROVED.value
        (supabase_client.table("cases")
            .update({"ai_decision": ai_decision})
            .eq("id", self.case_id)
            .execute()
        )

        self.violations = failure_codes


    def handle_verdict(self, title, message, approved):

        # notify the employee
        submitter_id = self.current_case_data['submitter_id']
        em.insert_notification(submitter_id, title, message)

        # email the employee
        employee_query = supabase_client.table("users").select("id, name, email").eq("id", submitter_id).limit(1).single().execute()
        employee = employee_query.data

        em.send_email(employee["email"], employee["name"], title, message, approved)

        # update case status in db
        status = Status.APPROVED.value if approved else Status.REJECTED.value
        resp = (
            supabase_client.table("cases")
            .update({"status": status})
            .eq("id", self.case_id)
            .execute()
        )


    @rx.event
    async def on_approve(self):

        self.handle_verdict("Blueprint Approved", "Your blueprint has been approved.", True)

        # display toast and redirect
        yield rx.toast.success("Blueprint approved!")
        yield rx.redirect("/assignments")


    @rx.event
    async def on_reject(self):

        self.handle_verdict("Blueprint Rejected", "Your blueprint has been rejected.", False)

        # display toast and redirect
        yield rx.toast.info("Blueprint rejected!")
        yield rx.redirect("/assignments")



    def update_current_case(self, case):
        # print(f'{case=}')
        self.case_id = case["id"]
        # print(f"loading case {self.case_id=}")
        violations_query = supabase_client.table("violations").select("guideline_code").eq("case_id", self.case_id).execute()

        self.violations = [row["guideline_code"] for row in violations_query.data]


    @rx.event
    async def load_data(self):
        # Loads the case data for the current user from the database
        try:
            user_state = await self.get_state(UserState)
            if user_state.role == "reviewer":
                all_cases = (
                    supabase_client.table("cases")
                    .select("*")
                    .eq("reviewer_id", user_state.user_id)
                    .execute()
                )
            else:
                all_cases = (
                    supabase_client.table("cases")
                    .select("*")
                    .eq("submitter_id", user_state.user_id)
                    .execute()
                )
                

            self.update_current_case(all_cases.data[0])

            self.case_data = all_cases.data
            self.listOfCases = [str(case["id"]) for case in self.case_data]

            guidelines_query = supabase_client.table("guidelines").select("*").execute()
            self.guidelines = guidelines_query.data
            self.case_result = self.case_data[0]["status"]

        except Exception as e:
            print("Exception in load_data:", e)
            traceback.print_exc()

    @rx.event
    def change_case(self, value: str):
        self.case_id = int(value)

        try:
            current_case = (
                supabase_client.table("cases")
                .select("*")
                .eq("id", self.case_id)
                .limit(1)
                .single()
                .execute()
            )

            self.update_current_case(current_case.data)





        except Exception as e:
            print("Exception in load current case:", e)
            traceback.print_exc()


    @rx.event
    async def on_validate(self):
        self.is_validating = True
        yield None
        await asyncio.sleep(1.5)

        # run validation
        print(self.current_case_data)

        try:
            failures = run_validation(
                self.current_case_data['blueprint_path'],
                self.current_case_data['submitter_id']
            )
        except FileNotFoundError as e:
            self.is_validating = False
            yield rx.toast.error('Blueprint file not available')
            return


        self.write_violations(failures)

        # TODO call visualizer code here to generate image

        self.is_validating = False
        yield rx.toast.info("AI Validation ran successfully")
        # hack to trigger the visualize_path to show the image
        self.vis_output_trigger += 1



    @rx.event
    def on_violation_delete(self, guideline_id: int):

        (supabase_client.table("violations")
            .delete()
            .eq("case_id", self.case_id)
            .eq("guideline_code", guideline_id)
            .execute()
        )

        self.violations = list(filter(lambda v: v != guideline_id, self.violations))

        return rx.toast.success("Removed violation")

    # @rx.event
    # def handle_comments(self, form_data: dict):
    #     # Store the comment locally
    #     self.comments = form_data
    #     # Update the comments column in the cases table for the selected case_id
    #     try:
    #         comment_text = form_data.get("comment", "")
    #         supabase_client.table("cases").update({"comments": comment_text}).eq("id", self.case_id).execute()
    #     except Exception as e:
    #         print("Exception in handle_comments:", e)

    @rx.event
    def no_op(self):
        pass

    @rx.var
    def compliance_score(self) -> str:
        if len(self.guidelines) == 0:
            score =  0.0
        else:
            score = (len(self.guidelines)- len(set(self.violations))) / len(self.guidelines)
        return f"{score * 100:.0f}%"



    @rx.var
    def violated_guidelines(self) -> list[dict]:
        # filter guidelines to be only those whose id is in the violated ids
        violated = list(filter(lambda g: g['id'] in self.violations, self.guidelines))
        print(f'{violated=}')
        return violated
    

    @rx.var
    def violations_count(self) -> int:
        return len(self.violated_guidelines)

    @rx.var
    def listOfCases_count(self) -> int:
        return len(self.listOfCases)




    @rx.var
    def current_case_data(self) -> Optional[dict]:
        # for case in self.case_data:
        #     print(f'{case['id']=}')

        filt = list(filter(lambda case: self.case_id == case['id'], self.case_data))
        filt = filt[0] if filt else None
        print(filt)
        return filt


    @rx.var
    def case_id_str(self) -> str:
        return str(self.case_id)

    @rx.var
    def case_display_text(self) -> str:
        if self.current_case_data:
            return f"File Name: {self.current_case_data['blueprint_path']}"
        else:
            return ""


    @rx.var
    def visualization_path(self) -> Optional[str]:
        # create dep on the trigger so that we can recompute
        # this var when we run ai validation
        _ = self.vis_output_trigger
        # N.B! This approach exposes blueprints publicly via assets.
        if not self.current_case_data:
            return None

        bp_name = self.current_case_data['blueprint_path']
        bp_submitter = self.current_case_data['submitter_id']
        vis_output = bp_name2vispath(bp_name, bp_submitter)

        if vis_output.exists():
            vis_output = Path(*vis_output.parts[1:])
            print(f"{vis_output=}")
            return str(vis_output)
        else:
            return None


def table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID"),
                rx.table.column_header_cell("Title"),
                rx.table.column_header_cell("Rule Description"),
                rx.table.column_header_cell("Category"),
                rx.match(
                    UserState.role,
                    ("reviewer", rx.table.column_header_cell("Actions")),
                    rx.fragment()  # Empty for non-reviewers
                )
            )
        ),
        rx.table.body(
            rx.foreach(
                AIValidationState.violated_guidelines,
                lambda item: rx.table.row(
                    rx.table.cell(item["id"]),
                    rx.table.cell(item["title"]),
                    rx.table.cell(item["description"]),
                    rx.table.cell(item["category"]),
                    rx.match(
                        UserState.role,
                        ("reviewer", rx.table.cell(
                            rx.button(
                                "Delete",
                                color_scheme="red",
                                on_click=AIValidationState.on_violation_delete(item["id"])
                            )
                        )),
                        rx.fragment()  # Empty for non-reviewers
                    )
                )
            )
        )
    )
        

    

def compliance_card() -> rx.Component:
    return rx.vstack(
        rx.script(src="https://unpkg.com/html2canvas-pro@1.5.11/dist/html2canvas-pro.js"),
        rx.script(src="/export-lib.js"),
        rx.cond(AIValidationState.violated_guidelines,
            # Top statistics cards
            rx.box(
                rx.vstack(
                    rx.hstack(
                        stat_card("Overall Compliance", AIValidationState.compliance_score, "circle-check-big", "green", "Compliance across all building guidelines."),
                        stat_card("Critical Violations", AIValidationState.violations_count, "circle-x", "#d62828", "High-priority issues requiring immediate attention."),
                        stat_card("Pending Reviews", AIValidationState.listOfCases_count, "hourglass", "#220bb4", "BlueprintsSections awaiting manual verification or dispute resolution."),
                        spacing="4",
                    ),
                    margin_bottom="2em"
                )
            ),
                rx.fragment()
        ),
                

        # Image + Table side-by-side
        rx.hstack(
                # Table Card
                rx.card(
                    rx.vstack(
                        rx.heading("Detailed Compliance Report", size="5"),
                        rx.hstack(
                            rx.input(
                                rx.input.slot(
                                    rx.icon(tag="search")
                                ),
                                placeholder="Search compliance items...",
                                width="400px"
                            ),
                            rx.button(rx.icon(tag="list-filter"), "Status")
                        ),
                        rx.cond(
                            ~AIValidationState.violated_guidelines,
                            rx.text("No violations to display.", size="3", color="gray"),
                            table()
                        ),
                        rx.match(
                            UserState.role,
                            ("reviewer", rx.vstack(
                                rx.heading("Add Comments", size="4"),
                                rx.form.root(
                                    rx.hstack(
                                        rx.input(
                                            name="input",
                                            placeholder="Enter text...",
                                            type="text",
                                            required=True,
                                            size="3",
                                            width="70%"
                                        ),
                                        rx.button("Add", type="submit")
                                    ),
                                    reset_on_submit=True
                                )
                            )),
                            rx.fragment()
                        )
                    ),
                
                    padding="10px"
                ),
                # Visualization image
                rx.box(
                    rx.cond(
                        AIValidationState.visualization_path,
                        rx.image(
                            src=rx.get_upload_url(AIValidationState.visualization_path),
                            width="100%",
                            height="auto",
                            object_fit="contain"
                        ),
                        rx.box(height="100%")  # Keeps height even if image is missing
                    ),
                    width="50%",
                    bg="gray.50",
                    padding="10px",
                    border_radius="8px"
                ),
                width="100%",
                spacing="4",
                margin_y="10px"
            ),
        # Download button
        rx.button(
            "Download Report",
            color_scheme="blue",
            on_click=rx.call_script("downloadPDF()", callback=AIValidationState.no_op)
        )
    )