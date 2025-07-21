import reflex as rx
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client

# State class to manage the case's progress for the current user
class CaseState(UserState):
    case_id: int = 0  # ID of the case, 0 if not loaded
    status: str = ""  # Status of the case (e.g., "pending")
    reviewer_id: int = 0  # ID of the reviewer, 0 if unassigned

    @rx.var
    def current_step(self) -> int:
        # Determines the current step in the progress tracker based on case data
        if not self.case_id:
            return 0  # No case uploaded
        elif self.status == "pending" and not self.reviewer_id:
            return 1  # Received, unassigned
        elif self.status == "pending" and self.reviewer_id:
            return 2  # Under Review
        else:
            return 3  # Review Completed

    @rx.event
    def load_caseData(self):
        # Loads the case data for the current user from the database
        try:
            user_id_int = int(str(self.user_id))
            response = (
                supabase_client.table("cases")
                .select("*")
                .eq("submitter_id", user_id_int)
                .single()
                .execute()
            )
            self.case_id = response.data["id"]
            self.status = response.data["status"]
            self.reviewer_id = response.data["reviewer_id"]
        except Exception as e:
            print("Exception in load_caseData:", e)

# Determines the status string for a given step in the progress tracker
def get_status(step_number: int, current_step: int, is_last: bool) -> str:
    return rx.cond(
        step_number < current_step,
        "completed",
        rx.cond(
            (step_number == current_step) & is_last,
            "completed",
            rx.cond(
                step_number == current_step,
                "current",
                "pending"
            )
        )
    )

# Returns style properties for the progress circle based on its status
def get_circle_style(status: str) -> dict:
    return {
        "background": rx.match(
            status,
            ("completed", "green"),
            ("current", "#220bb4"),
            ("pending", "gray"),
            "gray"
        ),
        "border": rx.match(
            status,
            ("completed", "2px solid green"),
            ("current", "2px solid blue"),
            ("pending", "2px solid #d1d5db"),
            "2px solid #d1d5db"
        ),
        "color": rx.match(
            status,
            ("completed", "white"),
            ("current", "white"),
            ("pending", "#6b7280"),
            "#6b7280"
        ),
    }

# Returns the color for the connecting line between steps
def get_line_color(status: str) -> str:
    return rx.match(
        status,
        ("completed", "green"),
        ("current", "#d1d5db"),
        ("pending", "#d1d5db"),
        "#d1d5db"
    )

# Returns the color for the step label
def get_label_color(status: str) -> str:
    return rx.match(
        status,
        ("completed", "green"),
        ("current", "blue"),
        ("pending", "#6b7280"),
        "#6b7280"
    )

# Renders a single progress circle (step) in the tracker
def progress_circle(
    step_number: int,
    label: str,
    current_step: int,
    is_last: bool = False
) -> rx.Component:
    status = get_status(step_number, current_step, is_last)  # Determine the status for this step
    circle_style = get_circle_style(status)  # Get the style for the circle
    line_color = get_line_color(status)      # Get the color for the connecting line
    label_color = get_label_color(status)    # Get the color for the label

    return rx.hstack(
        rx.vstack(
            rx.box(
                rx.cond(
                    status == "completed",
                    rx.text("✓", font_size="16px", font_weight="bold"),
                    rx.text(str(step_number), font_size="14px", font_weight="bold")
                ),
                width="40px",
                height="40px",
                border_radius="50%",
                display="flex",
                align_items="center",
                justify_content="center",
                transition="all 0.3s ease",
                z_index="1",
                **circle_style
            ),
            rx.text(
                label,
                font_size="12px",
                font_weight="500",
                color=label_color,
                text_align="center",
                margin_top="8px",
                white_space="nowrap"
            ),
            align_items="center",
            spacing="0",
            position="relative",
        ),
        rx.cond(
            not is_last,
            rx.box(
                width="100px",
                height="2px",
                background=line_color,
                margin_x="0px",
                position="relative",
                bottom="10px",
                transition="all 0.3s ease"
            ),
            rx.box()
        ),
        align_items="center",
        spacing="0",
    )

# Main component to render the progress tracker UI
def progress_tracker() -> rx.Component:
    return rx.vstack(
        rx.heading("Track Progress", size="4", margin_bottom="20px"),  # Title
        rx.hstack(
            # Render each step in the tracker
            progress_circle(1, "Received", CaseState.current_step),
            progress_circle(2, "Under Review", CaseState.current_step),
            progress_circle(3, "Completed", CaseState.current_step, is_last=True),
            align_items="flex-start",
            spacing="0",
            width="100%",
            justify_content="center",
        ),
        on_mount=CaseState.load_caseData,  # Load case data when the component mounts
        padding="40px",
        align_items="center",
        max_width="600px",
        margin="0 auto",
    )