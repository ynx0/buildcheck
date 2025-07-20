import reflex as rx
from buildcheck.components.stat_card import stat_card
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.backend.supabase_client import supabase_client


class GuidelineState(rx.State):
    guideline: list[str]  # Explicitly type as list of list of strings
    # I know that we should'nt use this table, but I'm only using it to get guidelines examples
    # When we finalize the DB schema, I will replace this with the correct table
    response = supabase_client.table("guidelines").select("*").execute()
    guideline = [
        [item.get("code"), item.get("title"), item.get("description"),item.get("category")]
        for item in response.data
    ]
class SelectState(rx.State):
    value: str = "444"

    @rx.event
    def change_bluePrint(self, value: str):
        self.value = value

def show_guideline(guideline: list):
    # Trigger guideline loading if needed (handled by State in Reflex)
    return rx.table.row(
        rx.table.cell(guideline[0]),
        rx.table.cell(guideline[1]),
        rx.table.cell(guideline[2]),
        rx.table.cell(status_tag("approved")),  # Assuming status is always "approved" for this example
        rx.table.cell(guideline[3]),
        rx.table.cell(rx.button("Delete", color_scheme="red")),
    )
class FormInputState(rx.State):
    form_data: dict = {}

    @rx.event
    def handle_submit(self, form_data: dict):
        self.form_data = form_data

def validation_page() -> rx.Component:
    return rx.vstack(
            navbar(),
            rx.hstack(
                rx.text("Blueprint ID:", font_weight="bold"),
                rx.select(
                    ["444", "555", "343"],
                    value=SelectState.value,
                    on_change=SelectState.change_bluePrint,
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
                stat_card("Overall Compliance", "92%", "circle-check-big", "green", "Compliance across all building guidelines."),
                stat_card("Critical Violations", "3", "circle-x", "#d62828", "High-priority issues requiring immediate attention."),
                stat_card("Minor Warnings", "12", "triangle-alert", "#ffde59", "Potential issues or areas for improvement."),
                stat_card("Pending Reviews", "5", "hourglass", "#220bb4", "BlueprintsSections awaiting manual verification or dispute resolution."),
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
                                GuidelineState.guideline, show_guideline
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
                    on_submit=FormInputState.handle_submit,
                    reset_on_submit=True,
                    ),
                ),
            ),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ), footer()
