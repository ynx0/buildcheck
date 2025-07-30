import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.components.complianceCard import compliance_card, AIValidationState


def guideline_status(guideline: str) -> rx.Component:
    return rx.cond(AIValidationState.violations.contains(guideline), status_tag("rejected"), status_tag("approved")) 


# def compliance_card() -> rx.Component:
#     return rx.card(
#         rx.vstack(
#             rx.heading("Detailed Compliance Report", size="5"),
#             rx.hstack(
#                 rx.input(
#                 rx.input.slot(
#                     rx.icon(tag="search"),
#                 ),
#                 placeholder="Search compliance items...",
#                 width="400px"
#                 ),
#                 rx.button(rx.icon(tag="list-filter"), "Status")
#             ),
#             rx.cond(
#                 ~AIValidationState.violated_guidelines,
#                 rx.text('No violations to display.', font_weight="bold", size="5"),
#                 rx.table.root(
#                     rx.table.header(
#                         rx.table.row(
#                             rx.table.column_header_cell("ID"),
#                             rx.table.column_header_cell("Title"),
#                             rx.table.column_header_cell("Rule Description"),
#                             # rx.table.column_header_cell("Status"),
#                             rx.table.column_header_cell("Category"),
#                             rx.table.column_header_cell("Actions"),
#                         )
#                     ),
#                     rx.table.body(
#                         rx.foreach(
#                             AIValidationState.violated_guidelines,
#                             lambda item: rx.table.row(
#                                 rx.table.cell(item["id"]),
#                                 rx.table.cell(item["title"]),
#                                 rx.table.cell(item["description"]),
#                                 # rx.table.cell(guideline_status(item["id"])),
#                                 rx.table.cell(item["category"]),
#                                 # TODO this button should delete
#                                 rx.table.cell(rx.button(
#                                     "Delete",
#                                     color_scheme="red",
#                                     on_click=AIValidationState.on_violation_delete(item['id'])
#                                 ))
#                             )
#                         )
#                     ),
#                 ),
#             ),

#             rx.heading("Add Comments", size="4"),
#             rx.form.root(
#             rx.hstack(
#                 rx.input(
#                     name="input",
#                     placeholder="Enter text...",
#                     type="text",
#                     required=True,
#                     size="3",
#                     width="70%",
#                 ),
#                 rx.button("Add", type="submit"),
#                 width="100%",
#             ),
#             reset_on_submit=True
#             ),
#         )
#     )


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
            compliance_card(),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ), footer()
