import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.status_tag import status_tag
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase_client
from typing import List




class EmployeeUploadState(rx.State):
    uploads: List[dict] = []


    @rx.event
    async def on_load(self):

        user = await self.get_state(UserState)
        response = (
            supabase_client.table("cases")
            .select("*")
            .eq("submitter_id", user.user_id)
            .execute()
        )

        self.uploads = response.data


    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("no files given")
            return

        yield rx.toast('uploading')

        # upload file locally
        file = files[0]
        data = await file.read()
        uid  = await self.get_var_value(UserState.user_id)
        user_dir = rx.get_upload_dir() / ('user_' + str(uid))
        user_dir.mkdir(parents=True, exist_ok=True)

        path = user_dir / file.name
        with path.open("wb") as f:
            f.write(data)

        # FIXME for now, we will hardcode a reviewer
        reviewer_resp = supabase_client.table("users").select("*").eq("role", "reviewer").limit(1).single().execute()
        reviewer_id = None
        if reviewer_resp.data:
            print('reviewer data', reviewer_resp.data)
            reviewer_id = reviewer_resp.data['id']
        else:
            yield rx.toast.warning("could not assign to reviewer")


        # create case
        response = supabase_client.table("cases").insert({
            "submitter_id": uid,
            "blueprint_path": file.name,
            "reviewer_id": reviewer_id,

        }).execute()

        if response.data:
            self.uploads += response.data
            # print("response was", response.data)

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
    def row(upload) -> rx.Component:
        return rx.table.row(
            rx.table.cell(upload["id"], justify="center"),
            rx.table.cell(upload["submitted_at"], justify="center"),
            rx.table.cell(upload["blueprint_path"], justify="center"),
            rx.table.cell(status_tag(upload["status"]), justify="center"),
            rx.table.cell(rx.link("view", href="/blueprint-pending"), justify="center"),
        )

    return rx.cond(
        ~EmployeeUploadState.uploads,
        rx.card(rx.text("No activity", color="gray", size="2", align="center"), width="100%", max_width="40em"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Blueprint ID", justify="center"),
                    rx.table.column_header_cell("Date", justify="center"),
                    rx.table.column_header_cell("File", justify="center"),
                    rx.table.column_header_cell("Status", justify="center"),
                    rx.table.column_header_cell("Actions", justify="center"),
                )
            ),
            rx.table.body(
                    rx.foreach(EmployeeUploadState.uploads, row),
            ),
            width="100%",
            max_width="80em",
            overflow_x="auto",
            padding="1em",
            variant="surface"
        )
    )




@rx.page(route='/upload', on_load=EmployeeUploadState.on_load)
def upload_page() -> rx.Component:
    return rx.fragment(
        rx.vstack(
            navbar(),
            rx.center(
                upload_card(),
                padding_y="4em"
            ),
            rx.heading("Recent Upload Activity", size="9", mt="3em"),
            rx.spacer(),
            upload_table(),
            spacing="3",
            align="center",
            padding="3",
        ),
        footer()
    )

