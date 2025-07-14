import reflex as rx
from ..components.stats_cards import stats_cards_group
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer
def validation_page() -> rx.Component:
    return rx.vstack(
            navbar(),
            stats_cards_group(),
            rx.box(
                width="100%",
            ),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ),footer(),
