import reflex as rx

class ProgressState(rx.State):
    current_step: int = 2  # 1: Received, 2: Under Review, 3: Review Completed
    
    def set_step(self, step: int):
        self.current_step = step

def get_status(step_number: int, current_step: int) -> str:
    return rx.cond(
        step_number < current_step,
        "completed",
        rx.cond(
            step_number == current_step,
            "current",
            "pending"
        )
    )

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

def get_line_color(status: str) -> str:
    return rx.match(
        status,
        ("completed", "green"),
        ("current", "#d1d5db"),
        ("pending", "#d1d5db"),
        "#d1d5db"
    )

def get_label_color(status: str) -> str:
    return rx.match(
        status,
        ("completed", "green"),
        ("current", "blue"),
        ("pending", "#6b7280"),
        "#6b7280"
    )

def progress_circle(
    step_number: int,
    label: str,
    current_step: int,
    is_last: bool = False
) -> rx.Component:
    status = get_status(step_number, current_step)
    circle_style = get_circle_style(status)
    line_color = get_line_color(status)
    label_color = get_label_color(status)

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

def progress_tracker() -> rx.Component:
    return rx.vstack(
        rx.heading("Blueprint Validation Progress", size="4", margin_bottom="30px",),
        rx.box(
            rx.hstack(
                progress_circle(1, "Received", ProgressState.current_step),
                progress_circle(2, "Under Review", ProgressState.current_step),
                progress_circle(3, "Review Completed", ProgressState.current_step, is_last=True),
                align_items="flex-start",
                spacing="0",
                width="100%",
                justify_content="center",
            ),
            width="100%",
            position="relative",
            padding_y="20px",
        ),
        align_items="center",
        spacing="4",
        padding="40px",
        max_width="600px",
        margin="0 auto",
    )
