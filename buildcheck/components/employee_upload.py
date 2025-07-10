import reflex as rx
from datetime import date

# Dummy data for table
uploads = [
    {"id": "444", "date": "2025-06-04", "status": "pending"},
    {"id": "411", "date": "2025-05-24", "status": "canceled"},
    {"id": "405", "date": "2024-09-14", "status": "approved"},
    {"id": "403", "date": "2024-08-29", "status": "rejected"},
]

def status_tag(status: str) -> rx.Component:
    colors = {
        "pending": "yellow",
        "approved": "green",
        "rejected": "red",
        "canceled": "gray",
    }
    return rx.badge(
        status,
        color_scheme=colors.get(status, "gray"),
        variant="soft",
        text_transform="capitalize"
    )

def navbar() -> rx.Component:
    return rx.hstack(
        rx.heading("🏗️ BuildCheck", size="6"),
        rx.spacer(),
        rx.link("Home", href="/"),
        rx.link("Status", href="/status"),
        rx.spacer(),
        rx.icon_button(rx.icon("bell"), variant="ghost"),
        rx.avatar(name="PV", size="3"),
        rx.button("Logout", size="3", variant="outline"),
        padding="1em",
        border_bottom="1px solid #eee"
    )

def upload_card() -> rx.Component:
    return rx.vstack(
        rx.heading("Upload Your Construction Plan", size="9"),
        rx.text("Select or drag your PDF plans for validation against Saudi building guidelines.", color="gray"),
        rx.box(
            rx.icon("upload", box_size=6),
            rx.text("Drag & drop your PDF plan here, or"),
            rx.button("Browse Files", size="3", mt="0.5em"),
            border="2px dashed #ccc",
            border_radius="md",
            padding="2em",
            align="center",
            width="100%"
        ),
        rx.text(
            "💡 Tip: For optimal validation, ensure your PDF plans are clear, high-resolution, and not password-protected. "
            "Our system strictly adheres to the latest Saudi building codes.",
            font_size="0.9em",
            color="gray"
        ),
        rx.button("📘 Building Guidelines", align_self="end", mt="1em", color_scheme="blue"),
        spacing="6",
        width="100%",
        max_width="40em",
        padding="2em",
        border="1px solid #eee",
        border_radius="lg",
        align="start",
    )



def upload_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Blueprint ID"),
                rx.table.column_header_cell("Date"),
                rx.table.column_header_cell("Status"),
                rx.table.column_header_cell("Actions"),
            )
        ),
        rx.table.body(
            *[
                rx.table.row(
                    rx.table.cell(upload["id"]),
                    rx.table.cell(upload["date"]),
                    rx.table.cell(status_tag(upload["status"])),
                    rx.table.cell(rx.link("view", href="#", color="blue")),
                )
                for upload in uploads
            ]
        ),
        width="100%",
        max_width="40em",
        overflow_x="auto",
        padding="1em",
        box_shadow="sm",
        border_radius="md",
        variant="surface"
    )



def footer() -> rx.Component:
    return rx.vstack(
        rx.heading("🏗️ BuildCheck", size="6"),
        rx.text("Made by ARCH Authors", font_size="0.7em", color="gray"),
        padding="2em",
        spacing="1"


@rx.page(route='/upload')
def upload_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.center(
            upload_card(),
            padding_y="4em"
        ),
        rx.heading("Recent Upload Activity", size="9", mt="3em"),
        upload_table(),
        footer(),
        spacing="3",
        align="center",
        padding="3",
    )
