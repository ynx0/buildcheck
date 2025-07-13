import reflex as rx
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer

class SelectState(rx.State):
    blueprint_id: str = "444"
    blueprintIds: list[str] = ["444", "555", "666"]

    @rx.event
    def change_blueprint(self, value: str):
        self.blueprint_id = value

def employee_blueprint1() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading("Overall Summary"),
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
                    rx.text("Your plan is currently under review. Please monitor your email for any updates.", size="4"),
                    rx.button("Resubmit", background_color="#197dca"),
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
    ), footer(),
 