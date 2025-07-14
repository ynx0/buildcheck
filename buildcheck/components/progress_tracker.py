import reflex as rx

class ProgressTrackerState(rx.State):
    current_status: str = "Received"  # Default status
    
@rx.event
def update_status(self, new_status: str):
    valid_statuses = ["Received", "Under Review", "Review Completed"]
    if new_status in valid_statuses:
        self.current_status = new_status

def progress_circle(title: str, is_active: bool, is_completed: bool) -> rx.Component:
    return rx.vstack(
        rx.circle(
            rx.cond(
                is_completed,
                rx.icon("check", color="white"),
                rx.text(title[0], color="white", font_size="sm")
            ),
            size="40px",
            bg=rx.cond(
                is_completed | is_active,
                "blue.500",
                "gray.300"
            ),
        ),
        rx.text(
            title,
            color=rx.cond(
                is_completed | is_active,
                "blue.500",
                "gray.500"
            ),
            font_weight="medium",
            font_size="sm",
        ),
        align="center",
        spacing="2",
    )

def progress_tracker() -> rx.Component:
    steps = ["Received", "Under Review", "Review Completed"]
    current_idx = steps.index(ProgressTrackerState.current_status)
    
    return rx.hstack(
        *[
            rx.box(
                progress_circle(
                    step,
                    is_active=(i == current_idx),
                    is_completed=(i < current_idx),
                ),
                flex="1",
                position="relative",
                _after=rx.cond(
                    i < len(steps) - 1,
                    {
                        "content": "''",
                        "position": "absolute",
                        "top": "20px",
                        "right": "-50%",
                        "width": "100%",
                        "height": "2px",
                        "background": rx.cond(
                            i < current_idx,
                            "blue.500",
                            "gray.300"
                        ),
                    },
                    {}
                )
            )
            for i, step in enumerate(steps)
        ],
        width="100%",
        padding_y="8",
        margin_y="4",
        justify="center",
        spacing="0",
    )