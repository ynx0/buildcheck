import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.backend.supabase_client import supabase_client
from buildcheck.state import user_state
from buildcheck.state.user_state import UserState


class EmployeeUploadState(rx.State):
    uploaded_file: str = ""
    uploads: list[dict] = []
    latest_status: str = "No uploads yet."

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No files selected.")
            return
        file = files[0]
        data = await file.read()
        path = rx.get_upload_dir() / file.name
        with path.open("wb") as f:
            f.write(data)

        self.uploaded_file = file.name
        yield rx.clear_selected_files("upload")
        yield rx.toast.success("Upload complete.")

    @rx.event
    async def load_uploads(self):
        try:
            user_state = await self.get_state(UserState)
            email = user_state.email

            # Fetch user ID
            user_response = supabase_client.table("users").select("id").eq("email", email).limit(1).execute()
            user_data = user_response.data[0] if user_response.data else None

            if not user_data:
                raise ValueError(f"No user found for email: {email}")

            user_id = user_data["id"]


            # Fetch uploaded blueprints by the user
            case_response = supabase_client.table("cases").select(
                "id, submitted_at, status, blueprint_path"
            ).eq("submitter_id", user_id).order("submitted_at", desc=True).execute()

            case_data = case_response.data or []


            for case in case_data:
                print(f"[DEBUG] Case: {case}")
            self.uploads = [
                {
                    "id": c.get("id"),
                    "date": c.get("submitted_at", "").split("T")[0],
                    "status": c.get("status", "").capitalize(),
                    "path": c.get("blueprint_path")
                }
                for c in case_data
            ]

            self.latest_status = self.uploads[0]["status"] if self.uploads else "No uploads yet."

        except Exception as e:
            print(f"[load_uploads ERROR] {e}")
            self.uploads = []
            self.latest_status = "Error loading status."


def upload_component() -> rx.Component:
    return rx.vstack(
        rx.upload(
            rx.vstack(
                rx.icon("cloud-upload", size=50),
                rx.button("Select File"),
                rx.text("Drag and drop PDF files or click to select"),
                align="center"
            ),
            id="upload",
            multiple=False,
            accept={"application/pdf": [".pdf"]},
        ),
        rx.text(rx.selected_files("upload")),
        rx.button(
            "Upload",
            on_click=EmployeeUploadState.handle_upload(rx.upload_files("upload"))
        ),
        align="center"
    )


def upload_card() -> rx.Component:
    return rx.vstack(
        rx.heading("Upload Your Construction Plan", size="8", align="center"),
        rx.text(
            "Select or drag your PDF plans for validation against Saudi building guidelines.",
            color="gray",
            align="center"
        ),
        upload_component(),
        rx.divider(),
        rx.text(
            "Tip: Ensure your PDF plans are high-resolution and not password-protected. "
            "We validate based on Saudi building codes.",
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
            rx.cond(
                EmployeeUploadState.uploads,
                rx.foreach(
                    EmployeeUploadState.uploads,
                    lambda upload: rx.table.row(
                        rx.table.cell(upload["id"], justify="center"),
                        rx.table.cell(upload["date"], justify="center"),
                        rx.table.cell(status_tag(upload["status"]), justify="center"),
                        rx.table.cell(rx.link("View", href="/blueprint-pending"), justify="center"),
                    )
                ),
                rx.table.row(
                    rx.table.cell("No activity found", col_span=4, justify="center")
                )
            )
        ),
        width="100%",
        max_width="40em",
        overflow_x="auto",
        padding="1em",
        variant="surface"
    )


@rx.page(route='/upload', on_load=EmployeeUploadState.load_uploads)
def upload_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.center(upload_card(), padding_y="4em"),
        rx.heading("Recent Upload Activity", size="9", mt="3em"),
        upload_table(),
        spacing="3",
        align="center",
        padding="3",
    ), 
footer()