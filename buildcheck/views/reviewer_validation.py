import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.components.complianceCard import compliance_card, AIValidationState


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
                rx.cond(AIValidationState.current_case_data,
                    rx.text(AIValidationState.case_display_text)
                ),
                rx.spacer(),
                rx.spacer(),
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
            compliance_card(),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ), footer()
