# buildcheck/views/EmployeeView2.py

import reflex as rx
import reflex_enterprise as rxe

from .navbar import navbar


def timeline_example():
    return rx.vstack(
        rxe.mantine.timeline(
            rxe.mantine.timeline.item(
                title="Step 1",
                bullet="•",
            ),
            rxe.mantine.timeline.item(
                title="Step 2",
                bullet="•",
            ),
            rxe.mantine.timeline.item(
                title="Step 3",
                bullet="•",
            ),
            active=1,
            bullet_size=24,
            line_width=2,
            color="blue",
        )
    )





# Sample compliance data
data = [
    {"category": "Structure", "status": "approved", "details": "Foundation Depth 1.2m meets 1.0m requirement"},
    {"category": "Safety", "status": "approved", "details": "Fire Exit Width 0.8m (1.0m required)"},
    {"category": "Zoning", "status": "rejected", "details": "Building Height 8.2m (10m maximum)"},
]

# State to hold selected blueprint
class BlueprintState(rx.State):
    selected: str = ""

    def set_blueprint(self, value: str):
        self.selected = value

class TimelineState(rx.State):
    active_step: int = 0  # 0 = Step 1, 1 = Step 2, 2 = Step 3

    def next_step(self):
        if self.active_step < 2:
            self.active_step += 1

def timeline_example() -> rx.Component:
    return rx.vstack(
        rxe.mantine.timeline(
            rxe.mantine.timeline.item(title="Received", bullet="•"),
            rxe.mantine.timeline.item(title="Under Review", bullet="•"),
            rxe.mantine.timeline.item(title="Reviewed", bullet="•"),
            active=TimelineState.active_step,
            bullet_size=24,
            line_width=2,
            color="blue",
        ),
        rx.button("Advance Step", on_click=TimelineState.next_step, color_scheme="blue")
    )
            
def get_status_tag(status: str) -> rx.Component:
    color = "#dcfce7" if status == "approved" else "#fee2e2"
    text_color = "green" if status == "approved" else "red"
    return rx.box(
        rx.text(status, color=text_color, font_weight="medium", font_size="sm"),
        background_color=color,
        border_radius="xl",
        padding_x="2",
        padding_y="0.5",
        display="inline-block"
    )


def employee_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            navbar(),

            rx.hstack(
                rx.heading("Overall Summary", size="4", margin_top="1"),
                timeline_example(),
                justify="between",
                width="100%"
            ),

            rx.text("Blueprint", font_size="lg", font_weight="medium", margin_top="2"),

            # Dropdown + Timeline Row
            rx.hstack(
                # Left: DroSpdown and button
                rx.vstack(
                    rx.select(
                        items=["403", "404", "405"],
                        placeholder="Select Blueprint",
                        width="200px",
                        on_change=BlueprintState.set_blueprint,
                    ),
                    rx.button("View Blueprint", color_scheme="blue", margin_top="0.5"),
                    spacing="1"
                ),

                # Right: Timeline Progress
            #     rx.hstack(
            #         rx.vstack(
            #             rx.box(
            #                 rx.icon(tag="check", color="white", size=14),
            #                 background_color="blue",
            #                 border_radius="9999px",  # fully rounded
            #                 width="2",
            #                 height="2",
            #                 display="flex",
            #                 align_items="center",
            #                 justify_content="center",
            #             ),

            #             rx.text("Received", font_size="sm", margin_top="0.3"),
            #             align_items="center"
            #         ),
            #         rx.box(width="2", height="2px", bg="gray"),
            #         rx.vstack(
            #             rx.box(
            #                 rx.icon(tag="check", color="white", size=14),
            #                 background_color="blue",
            #                 border_radius="9999px",  # fully rounded
            #                 width="2",
            #                 height="2",
            #                 display="flex",
            #                 align_items="center",
            #                 justify_content="center",
            #             ),

            #             rx.text("Under Review", font_size="sm", margin_top="0.3"),
            #             align_items="center"
            #         ),
            #         rx.box(width="2", height="2px", bg="gray"),
            #         rx.vstack(
            #             rx.box(
            #                 rx.icon(tag="check", color="white", size=14),
            #                 background_color="blue",
            #                 border_radius="9999px",  # fully rounded
            #                 width="2",
            #                 height="2",
            #                 display="flex",
            #                 align_items="center",
            #                 justify_content="center",
            #             ),

            #             rx.text("Reviewed", font_size="sm", margin_top="0.3"),
            #             align_items="center"
            #         ),
            #         spacing="1",
            #         align_items="center",
            #         margin_left="4"
            #     ),
            #     spacing="6",
            #     margin_top="1",
            #     width="100%",
            #     justify="between"
            ),

            # Main Content Box
            rx.box(
                rx.vstack(
                    # Alert Box
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="triangle_alert", color="orange", size=24),
                            rx.vstack(
                                rx.text("Partial Compliance", font_weight="bold", font_size="lg"),
                                rx.text(
                                    "Your plans meet most requirements but need some adjustments.",
                                    font_size="sm",
                                    color="gray",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            spacing="2",
                            align="center"
                        ),
                        rx.hstack(
                            rx.box(
                                rx.text("78%", font_weight="bold", font_size="2xl", color="green"),
                                rx.text("Compliance Score", font_size="sm", color="gray"),
                                text_align="center",
                            ),
                            rx.box(
                                rx.text("12", font_weight="bold", font_size="2xl", color="blue"),
                                rx.text("Passed Checks", font_size="sm", color="gray"),
                                text_align="center",
                            ),
                            rx.box(
                                rx.text("3", font_weight="bold", font_size="2xl", color="orange"),
                                rx.text("Warnings", font_size="sm", color="gray"),
                                text_align="center",
                            ),
                            rx.box(
                                rx.text("2", font_weight="bold", font_size="2xl", color="red"),
                                rx.text("Violations", font_size="sm", color="gray"),
                                text_align="center",
                            ),
                            spacing="6",
                            justify="center",
                            width="100%",
                            margin_top="3"
                        ),
                        spacing="4",
                        background_color="#F0F4FF",
                        padding="4",
                        border_radius="lg",
                        width="100%",
                        margin_y="3"
                    ),

                    # Compliance Table
                    rx.data_table(
                        data=[{**item, "status": get_status_tag(item["status"])} for item in data],
                        columns=[
                            {"header": "Category", "accessor_key": "category"},
                            {"header": "Status", "accessor_key": "status"},
                            {"header": "Details", "accessor_key": "details"},
                        ],
                        pagination=True,
                        search=True,
                        width="100%",
                    ),

                    # Next Steps
                    rx.box(
                        rx.text("Next Steps", font_weight="bold", margin_top="1"),
                        rx.unordered_list(
                            rx.list_item("Revise fire exit width to meet minimum 1.0m requirement"),
                            rx.list_item("Add an additional parking space to meet local code"),
                            rx.list_item("Document window dimensions for emergency egress"),
                            rx.list_item("Resubmit revised plans for validation"),
                        ),
                        background_color="#F0F4FF",
                        padding="1",
                        border_radius="md",
                        width="100%"
                    ),

                    rx.button("Download Report", color_scheme="blue", margin_top="1.5")
                ),
                border="1px solid #ccc",
                border_radius="lg",
                padding="2",
                width="100%",
                background_color="white"
            )
        ),
        padding="2",
        width="100%"
    )
