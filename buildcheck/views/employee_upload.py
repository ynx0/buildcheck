import reflex as rx
from datetime import date

# Dummy data for table
uploads = [
    {"id": "444", "date": "2025-06-04", "status": "pending"},
    {"id": "411", "date": "2025-05-24", "status": "canceled"},
    {"id": "405", "date": "2024-09-14", "status": "approved"},
    {"id": "403", "date": "2024-08-29", "status": "rejected"},
]


# TODO the file handling works but is very rough right now
#      it doesn't do anything after the file has successfully uploaded.
class EmployeeUploadState(rx.State):
    uploaded_file: str = ""

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("no files given")
            return

        yield rx.toast('uploading')
        file = files[0]
        data = await file.read()
        path = rx.get_upload_dir() / file.name
        with path.open("wb") as f:
            f.write(data)
        self.uploaded_file = file.name
        yield rx.clear_selected_files("upload")
        yield rx.toast('done')


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






def upload_component() -> rx.Component:
    return rx.vstack(
            rx.upload(
                rx.vstack(
                    rx.icon("cloud-upload", size=50),
                    rx.button(
                        "Select File",
                        # border=f"1px solid {color}",
                    ),
                    rx.text("Drag and drop files here or click to select files"),

                    align="center"
                ),
                id="upload",
                multiple=False,
                accept={
                    "application/pdf": [".pdf"]
                },
            ),
            rx.text(rx.selected_files("upload")),
            rx.button(
                "Upload",
                on_click=EmployeeUploadState.handle_upload(
                    rx.upload_files("upload")
                ),
            ),
            align="center"
        )



def upload_card() -> rx.Component:
    return rx.vstack(
        rx.heading("Upload Your Construction Plan", size="9", align="center"),
        rx.text("Select or drag your PDF plans for validation against Saudi building guidelines.", color="gray", align="center"),
        upload_component(),
        rx.divider(),
        rx.text(
            "💡 Tip: For optimal validation, ensure your PDF plans are clear, high-resolution, and not password-protected. "
            "Our system strictly adheres to the latest Saudi building codes.",
            font_size="0.9em",
            color="gray"
        ),
        spacing="6",
        width="100%",
        max_width="40em",
        padding="2em",
        border="1px solid #eee",
        border_radius="lg",
        align="center",
    )



def upload_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Blueprint ID", justify="center"),
                rx.table.column_header_cell("Date", justify="center"),
                rx.table.column_header_cell("Status", justify="center"),
                rx.table.column_header_cell("Actions", justify="center"),
            )
        ),
        rx.table.body(
            *[
                rx.table.row(
                    rx.table.cell(upload["id"], justify="center"),
                    rx.table.cell(upload["date"], justify="center"),
                    rx.table.cell(status_tag(upload["status"]), justify="center"),
                    rx.table.cell(rx.link("view", href="#"), justify="center"),
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
    return rx.hstack(
        rx.heading("🏗️ BuildCheck", size="6"),
        rx.spacer(),
        rx.text("Made by ARCH Authors", font_size="0.7em", color="gray"),
        rx.spacer(),
        rx.button(
            rx.hstack(
                rx.icon("download"),
                rx.text("Building Guidelines", size="3"),
            ),
            align_self="end",
            mt="1em",
            color_scheme="blue",
            on_click=rx.download(url="/sbc201.pdf")
        ),
        padding="2em",
        spacing="5",
    )


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
