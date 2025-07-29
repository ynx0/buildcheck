import reflex as rx
from buildcheck.components.stat_card import stat_card
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client
import buildcheck.backend.email_utils as em
import traceback
from enum import Enum
from buildcheck.backend.validation import run_validation_employee
import asyncio
from typing import Optional
from buildcheck.backend.validation import Failure


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
    comments: dict = {}
    is_validating: bool = False


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

        (supabase_client.table("violations")
            .select("*")
            .eq("case_id", self.case_id)
            .execute()
        )


        # insert all the violations for current case
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
            all_cases = (
                supabase_client.table("cases")
                .select("*")
                .eq("reviewer_id", user_state.user_id)
                .execute()
            )

            self.update_current_case(all_cases.data[0])

            self.case_data = all_cases.data
            self.listOfCases = [str(case["id"]) for case in self.case_data]

            guidelines_query = supabase_client.table("guidelines").select("*").execute()
            self.guidelines = guidelines_query.data

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

        failures = run_validation_employee(
            self.current_case_data['blueprint_path'],
            self.current_case_data['submitter_id']
        )
        self.write_violations(failures)

        # TODO call visualizer code here to generate image

        self.is_validating = False
        yield rx.toast.info("AI Validation ran successfully")



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
    def current_case_data(self) -> Optional[dict]:
        # for case in self.case_data:
        #     print(f'{case['id']=}')

        filt = list(filter(lambda case: self.case_id == case['id'], self.case_data))
        filt = filt[0] if filt else None
        return filt


    @rx.var
    def case_id_str(self) -> str:
        return str(self.case_id)


    @rx.var
    def visualization_path(self) -> Optional[str]:
        if not self.current_case_data:
            return None

        bp_name = self.current_case_data['blueprint_path']
        bp_submitter = self.current_case_data['submitter_id']
        vis_output = bp_name2vispath(bp_name, bp_submitter)

        if vis_output.exists:
            s = str(vis_output)
            print(f"{vis_output=} {s=}")
            return '/' + s
        else:
            return None






def guideline_status(guideline: str) -> rx.Component:
    return rx.cond(AIValidationState.violations.contains(guideline), status_tag("rejected"), status_tag("approved")) 

@rx.page('/validation', on_load=AIValidationState.load_data)
def validation_page() -> rx.Component:
    return rx.vstack(
            navbar(),
            rx.hstack(
                rx.text("Blueprint ID:", font_weight="bold"),
                rx.select(
                    AIValidationState.listOfCases,
                    value=AIValidationState.case_id_str,
                    on_change=AIValidationState.change_case,
                    width="200px"
                ),
                rx.button(
                    "Approve",
                    color_scheme="blue",
                    on_click=AIValidationState.on_approve
                ),
                rx.button(
                    "Reject",
                    color_scheme="red",
                    on_click=AIValidationState.on_reject
                ),
                rx.spacer(),
                rx.button(
                    "Run AI Validation",
                    color_scheme="orange",
                    on_click=AIValidationState.on_validate,
                    loading=AIValidationState.is_validating
                ),
                margin="15px"
            ),
            rx.heading("AI Compliance Overview", size="6"),
            rx.hstack(
                stat_card("Overall Compliance", AIValidationState.compliance_score, "circle-check-big", "green", "Compliance across all building guidelines."),
                stat_card("Critical Violations", AIValidationState.violations.length(), "circle-x", "#d62828", "High-priority issues requiring immediate attention."),
                stat_card("Pending Reviews", AIValidationState.listOfCases.length(), "hourglass", "#220bb4", "BlueprintsSections awaiting manual verification or dispute resolution."),
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
                ),
            ),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ), footer()
