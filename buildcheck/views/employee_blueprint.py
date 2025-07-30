import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.progress_tracker import progress_tracker, CaseState
from buildcheck.backend.supabase_client import supabase_client
from buildcheck.components.complianceCard import compliance_card, ValidationState

def statusOfCase() -> rx.Component:
    # This function returns a UI component that displays the current status of the user's blueprint submission.
    return rx.cond( # If no blueprint has been uploaded (case_id is empty string), prompt the user to upload one.
        CaseState.case_id == "",
        rx.text("You did not upload a blueprint. Please upload a blueprint to view the status.", size="4"),
        # If a blueprint exists and is assigned to a reviewer (status is 'pending' and reviewer_id is set),
        # inform the user that the plan is under review.
        rx.cond(
            (CaseState.status == "pending") & (CaseState.reviewer_id),
            rx.text("Your plan is currently under review. Please monitor your email for any updates.", size="4"),
            # If a blueprint exists but is not yet assigned to a reviewer (status is 'pending'),
            # inform the user to wait for assignment.
            rx.cond(
                (CaseState.status == "pending"),
                rx.text("Your plan is unassigned. Please wait for a reviewer to be assigned.", size="4"),
                # Otherwise, the plan has been reviewed and the user can proceed with next steps.
                rx.text("Your plan has been reviewed. You can proceed with the next steps.", size="4")
            )
        )
    )
            
@rx.page('/blueprint-pending')
def employee_blueprint() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading("Overall Summary"),
        progress_tracker(),
        rx.hstack(
            rx.text("Blueprint ID:", size="4"),
            rx.box(
                CaseState.case_id,
                width="100px",
                border="2px solid #ccc",
                border_radius="4px",
                text_align="center",
            ),
        ),
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.heading("Compliance Report", size="5"),
                    statusOfCase(),
                    rx.cond(CaseState.current_step == 3, 
                        rx.vstack(
                            rx.hstack(
                            rx.icon(tag="triangle_alert", color="orange", size=20),
                            rx.vstack(
                                rx.text(f'This blueprint is {ValidationState.case_result.upper()}', font_size="lg", font_weight="bold"),
                                spacing="1"
                            ),
                            spacing="4",
                            align_items="start"
                            ),
                            compliance_card(), 
                        ),
                        rx.button("Resubmit", background_color="#197dca", size="3", marginTop="2em", on_click=rx.redirect("/upload"))
                    ),
                ),
                rx.image(
                    src="/blueprint.jpg",
                    alt="Blueprint Image",
                    width="50%",
                )
            ),
            padding="2em",
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    ), footer()
