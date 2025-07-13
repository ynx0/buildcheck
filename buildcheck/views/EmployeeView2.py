import reflex as rx
import reflex_enterprise as rxe

# from reflex.components.mantine.steps import steps, step
from .navbar import navbar

# Sample compliance data
compliance_data = [
    {"category": "Structure", "status": "approved", "details": "Foundation Depth 1.2m meets 1.0m requirement"},
    {"category": "Safety", "status": "approved", "details": "Fire Exit Width 0.8m (1.0m required)"},
    {"category": "Zoning", "status": "rejected", "details": "Building Height 8.2m (10m maximum)"},
]

# Blueprint selection state
class BlueprintState(rx.State):
    selected: str = ""

    def set_blueprint(self, value: str):
        self.selected = value

# Timeline progress state
class TimelineState(rx.State):
    active_step: int = 0  # 0 = Received, 1 = Under Review, 2 = Reviewed

    def next_step(self):
        if self.active_step < 2:
            self.active_step += 1

# Status tag helper
def get_status_tag(status: str) -> rx.Component:
    return rx.box(
        rx.text(
            status,
            color=rx.cond(status == "approved", "green", "red"),
            font_weight="medium",
            font_size="sm"
        ),
        background_color=rx.cond(status == "approved", "#dcfce7", "#fee2e2"),
        border_radius="xl",
        padding_x="2",
        padding_y="1",
        display="inline-block"
    )

# Timeline visual



def timeline_example() -> rx.Component:
    return rx.hstack(
        rxe.mantine.timeline(
            rxe.mantine.timeline.item(title="Received", bullet="•"),
            rxe.mantine.timeline.item(title="Under Review", bullet="•"),
            rxe.mantine.timeline.item(title="Reviewed", bullet="•"),
            active=TimelineState.active_step,
            bullet_size=24,
            line_width=2,
            color="blue",
            orientation="horizontal",
        ),
        # rx.button("Advance Step", on_click=TimelineState.next_step, color_scheme="blue", margin_top="2")
    )

# def timeline_example() -> rx.Component:
#     return rx.hstack(
#         rxe.steps(
#             rx.step(label="Received"),
#             rx.step(label="Under Review"),
#             rx.step(label="Reviewed"),
#             active=TimelineState.active_step,
#             color="blue",
#         ),
#         rx.button(
#             "Advance Step",
#             on_click=TimelineState.next_step,
#             color_scheme="blue",
#             margin_top="2",
#         ),
#     )





# Employee View Main Page
def employee_view() -> rx.Component:
    return rx.center(
        rx.box(
            rx.vstack(
                navbar(),

                # Wrapped compliance report inside bordered box
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Compliance Report", size="5", margin_top="2"),
                            rx.spacer(),
                            timeline_example(),
                            justify="between",
                            spacing="4",
                            width="100%",
                            align_items="center",
                            # alighn_items="start",
                            margin_bottom="3"
                        ),

                        rx.hstack(
                            rx.select(
                                items=["403", "404", "405"],
                                placeholder="Select Blueprint",
                                width="200px",
                                on_change=BlueprintState.set_blueprint,
                            ),
                            rx.button("View Blueprint", color_scheme="blue"),
                            spacing="4",
                            margin_bottom="4"
                        ),

                        # Compliance Summary Card
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
                                        rx.text("78%",
                                                font_weight="bold",
                                                style={"fontSize": "2rem"},
                                                color="green"),

                                        rx.text("Compliance Score", font_size="sm", color="gray"),
                                        text_align="center"
                                    ),
                                    rx.box(
                                        rx.text("12",
                                                font_weight="bold",
                                                style={"fontSize": "2rem"},
                                                color="blue"),

                                        rx.text("Passed Checks", font_size="sm", color="gray"),
                                        text_align="center"
                                    ),
                                    rx.box(
                                        rx.text("3",
                                                font_weight="bold",
                                                style={"fontSize": "2rem"},
                                                color="orange"),
                                        rx.text("Warnings", font_size="sm", color="gray"),
                                        text_align="center"
                                    ),
                                    rx.box(
                                        rx.text("2",
                                                font_weight="bold",
                                                style={"fontSize": "2rem"},
                                                color="red"),
                                        rx.text("Violations", font_size="sm", color="gray"),
                                        text_align="center"
                                    ),
                                    spacing="4",
                                    justify="center",
                                    width="100%",
                                    margin_top="3",

                                ),
                                spacing="4",
                                background_color="#F0F4FF",
                                padding="4",
                                width="100%",
                            ),
                            width="100%",
                            align_self="stretch",
                            border_radius="md",
                            margin_bottom="4",
                            padding="4",
                            
                        ),

                        # Updated Compliance Table with label, borders
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Category"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Details"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    compliance_data,
                                    lambda item: rx.table.row(
                                        rx.table.cell(item["category"]),
                                        rx.table.cell(get_status_tag(item["status"])),
                                        rx.table.cell(item["details"]),
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

                        # Next Steps
                        rx.box(
                            rx.text("Next Steps", font_weight="bold", margin_top="3"),
                            rx.unordered_list(
                                rx.list_item("Revise fire exit width to meet minimum 1.0m requirement"),
                                rx.list_item("Add an additional parking space to meet local code requirements"),
                                rx.list_item("Verify and document bedroom window dimensions for emergency egress"),
                                rx.list_item("Resubmit revised plans for validation"),
                            ),
                            background_color="#F0F4FF",
                            padding="4",
                            border_radius="md",
                            margin_top="3",
                            width="100%"
                        ),

                        rx.button("Download Report", color_scheme="blue", margin_top="3")
                    ),
                    padding="2em",
                    background_color="#F7F7F7",  # Light background
                    border="1px solid #ccc",      # Light border
                    border_radius="lg",           # Rounded corners
                    box_shadow="sm",              # Soft shadow
                    width="100%",
                    margin_top="2"
                ),
            ),
            padding="2em",
            width="100%",
        ),
        padding="2em"
    )
