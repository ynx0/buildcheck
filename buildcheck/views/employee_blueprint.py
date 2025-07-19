import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
from buildcheck.components.progress_tracker import progress_tracker
from buildcheck.state.user_state import UserState
from buildcheck.backend.supabase_client import supabase

class SelectState(UserState):
    blueprint_id: str = ""
    blueprintIds: list[str] = []
    response_data: list[dict] = []

    def on_load(self):
        #Load blueprints when the state is initialized
        print("Loading blueprints for user:", self.user_id)
        if self.user_id:
            # Fetch blueprints for the current user
            response = supabase.table("blueprints").select("*").eq("user_id", self.user_id).execute()
            print(response.data)
            self.response_data = response.data if response.data else []
            self.blueprintIds = [item["id"] for item in self.response_data] if self.response_data else []
            self.blueprint_id = self.response_data[-1]["id"] if self.response_data else ""

    @rx.event
    def change_blueprint(self, value: str):
        self.blueprint_id = value

    def statusOfBlueprint(self) -> str:
        if not self.blueprint_id:
            return "You did not upload a blueprint. Please upload a blueprint to view the status."
        
        # Find the blueprint with matching ID
        blueprint = next((item for item in self.response_data if item["id"] == self.blueprint_id), None)
        
        if not blueprint:
            return "Blueprint not found."
        
        status = blueprint.get("status", "")
        
        if status == "under_review":
            return "Your plan is currently under review. Please monitor your email for any updates."
        elif status == "unassigned":
            return "Your plan is unassigned. Please wait for a reviewer to be assigned."
        else:
            return "Your plan has been reviewed. You can proceed with the next steps."

def employee_blueprint() -> rx.Component:
    return rx.vstack(
        rx.box(on_mount=SelectState.on_load, style={"display": "none"}),
        navbar(),
        rx.heading("Overall Summary"),
        progress_tracker(),
        rx.hstack(rx.text("Blueprint ID:", size="4",),
        rx.select(
            SelectState.blueprintIds,
            value=SelectState.blueprint_id,
            on_change=SelectState.change_blueprint,
            width="200px",
        ),),
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.heading("Compliance Report", size="5"),
                    rx.text(SelectState.statusOfBlueprint(), size="4"),
                    rx.button("Resubmit", background_color="#197dca", size="3", marginTop="2em", on_click=rx.redirect("/upload")),
                ),
                rx.image(
                    src="./blueprint.jpg",
                    alt="Blueprint Image",
                    width="50%",)
            ),
            padding="2em",
            width="100%",
        ),
        width="100%",
        spacing="6",
        padding_x=["1.5em", "1.5em", "3em"],
    ), footer()
