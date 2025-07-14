import reflex as rx

class ProgressState(rx.State):
    current_step: int = 2  # 1: Received, 2: Under Review, 3: Review Completed
    
    def set_step(self, step: int):
        self.current_step = step

def progress_circle(
    step_number: int,
    label: str,
    current_step: int,
    is_last: bool = False
) -> rx.Component:
    #Create a progress circle with connecting line
    
    # Determine circle state
    is_completed = step_number < current_step 
    is_current = step_number == current_step
    is_pending = step_number > current_step
    
    # Circle styling based on state
    circle_bg = rx.cond(
        is_completed,
        "green",
        rx.cond(
            is_current,
            "#220bb4",
            "gray"
        )
    )
    
    circle_border = rx.cond(
        is_completed,
        "2px solid green",
        rx.cond(
            is_current,
            "2px solid blue",
            "2px solid #d1d5db"
        )
    )
    
    text_color = rx.cond(
        is_completed,
        "white",
        rx.cond(
            is_current,
            "white",
            "#6b7280"
        )
    )
    
    # Line styling
    line_color = rx.cond(
        is_completed,
        "green",
        "#d1d5db"
    )
    
    return rx.hstack(
        # Circle with label in vstack
        rx.vstack(
            rx.box(
                rx.cond(
                    is_completed,
                    rx.text("✓", font_size="16px", font_weight="bold"),
                    rx.text(str(step_number), font_size="14px", font_weight="bold")
                ),
                width="40px",
                height="40px",
                border_radius="50%",
                background=circle_bg,
                border=circle_border,
                display="flex",
                align_items="center",
                justify_content="center",
                color=text_color,
                transition="all 0.3s ease",
                z_index="1",  # Ensure circle is above the line
            ),
            # Label
            rx.text(
                label,
                font_size="12px",
                font_weight="500",
                color=rx.cond(
                    is_current,
                    "blue",
                    rx.cond(
                        is_completed,
                        "green",
                        "#6b7280"
                    )
                ),
                text_align="center",
                margin_top="8px",
                white_space="nowrap"
            ),
            align_items="center",
            spacing="0",
            position="relative",  # For proper line positioning
        ),
        # Connecting line (if not last step)
        rx.cond(
            not is_last,
            rx.box(
                width="100px",
                height="2px",
                background=line_color,
                margin_x="0px",  # Remove horizontal margin
                position="relative",
                bottom="10px",  # Align with circle center
                transition="all 0.3s ease"
            ),
            rx.box()  # Empty box for last step
        ),
        align_items="center",  # Center align items vertically
        spacing="0",
    )

def progress_tracker() -> rx.Component:
    return rx.vstack(
        rx.heading("Blueprint Validation Progress", size="4", margin_bottom="30px",),
        
        # Progress tracker container
        rx.box(
            rx.hstack(
                progress_circle(1, "Received", ProgressState.current_step),
                progress_circle(2, "Under Review", ProgressState.current_step),
                progress_circle(3, "Review Completed", ProgressState.current_step, is_last=True),
                align_items="flex-start",
                spacing="0",
                width="100%",
                justify_content="center",  # Center the entire progress tracker
            ),
            width="100%",
            position="relative",
            padding_y="20px",  # Add some vertical padding
        ),
        
        align_items="center",
        spacing="4",
        padding="40px",
        max_width="600px",
        margin="0 auto",
    )
