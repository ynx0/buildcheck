import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag


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
        yield rx.toast.success('done')








def upload_component() -> rx.Component:
    return rx.vstack(
            rx.upload(
                rx.vstack(
                    rx.icon("cloud-upload", size=50),
                    rx.button(
                        "Select File",
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
        rx.heading("Upload Your Construction Plan", size="8", align="center"),
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
                    rx.table.cell(rx.link("view", href="/blueprint-pending"), justify="center"),
                )
                for upload in uploads
            ]
        ),
        width="100%",
        max_width="40em",
        overflow_x="auto",
        padding="1em",
        variant="surface"
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
        spacing="3",
        align="center",
        padding="3",
    ), footer()

