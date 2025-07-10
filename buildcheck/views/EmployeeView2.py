# buildcheck/views/EmployeeView2.py

import reflex as rx
from .navbar import navbar

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


def employee_view() -> rx.Component:
    return rx.container(
        rx.vstack(
            navbar(),

            rx.heading("Overall Summary", size="4", margin_top="1"),
            rx.text("Blueprint", font_size="lg", font_weight="medium", margin_top="2"),

            # Dropdown + Timeline Row
            rx.hstack(
                # Left: Dropdown and button
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
                rx.hstack(
                    rx.vstack(
                        rx.box(
                            rx.icon(tag="check", color="white", size=14),
                            background_color="blue",
                            border_radius="9999px",  # fully rounded
                            width="2",
                            height="2",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),

                        rx.text("Received", font_size="sm", margin_top="0.3"),
                        align_items="center"
                    ),
                    rx.box(width="2", height="2px", bg="gray"),
                    rx.vstack(
                        rx.box(
                            rx.icon(tag="check", color="white", size=14),
                            background_color="blue",
                            border_radius="9999px",  # fully rounded
                            width="2",
                            height="2",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),

                        rx.text("Under Review", font_size="sm", margin_top="0.3"),
                        align_items="center"
                    ),
                    rx.box(width="2", height="2px", bg="gray"),
                    rx.vstack(
                        rx.box(
                            rx.icon(tag="check", color="white", size=14),
                            background_color="blue",
                            border_radius="9999px",  # fully rounded
                            width="2",
                            height="2",
                            display="flex",
                            align_items="center",
                            justify_content="center",
                        ),

                        rx.text("Reviewed", font_size="sm", margin_top="0.3"),
                        align_items="center"
                    ),
                    spacing="1",
                    align_items="center",
                    margin_left="4"
                ),
                spacing="6",
                margin_top="1",
                width="100%",
                justify="between"
            ),

            # Main Content Box
            rx.box(
                rx.vstack(
                    # Alert Box
                    rx.box(
                        rx.hstack(
                            rx.icon(tag="triangle_alert", color="orange"),
                            rx.text(
                                "Partial Compliance: Your plans meet most requirements but need some adjustments.",
                                font_weight="medium",
                            ),
                        ),
                        background_color="#FFFBEA",
                        padding="1",
                        border_radius="md",
                        border="1px solid #F6E05E",
                        margin_bottom="1"
                    ),

                    # Score Summary
                    rx.hstack(
                        rx.box(
                            rx.text("Compliance Score", font_weight="bold"),
                            rx.text("78%", color="green"),
                            border="1px solid #ddd",
                            padding="1",
                            border_radius="md"
                        ),
                        rx.box(
                            rx.text("Passed Checks", font_weight="bold"),
                            rx.text("12"),
                            border="1px solid #ddd",
                            padding="1",
                            border_radius="md"
                        ),
                        rx.box(
                            rx.text("Warnings", font_weight="bold"),
                            rx.text("3"),
                            border="1px solid #ddd",
                            padding="1",
                            border_radius="md"
                        ),
                        rx.box(
                            rx.text("Violations", font_weight="bold"),
                            rx.text("2", color="red"),
                            border="1px solid #ddd",
                            padding="1",
                            border_radius="md"
                        ),
                        spacing="6",
                        margin_y="1"
                    ),

                    # Compliance Table
                    rx.data_table(
                        data=data,
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
