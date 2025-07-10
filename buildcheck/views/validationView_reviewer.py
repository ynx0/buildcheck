"I'm going to edit this template later"
import reflex as rx
from ..components.stats_cards import stats_cards_group
from .navbar import navbar
from .table import main_table

def validation_page() -> rx.Component:
    my_child = rx.vstack(
            navbar(),
            stats_cards_group(),
            rx.box(
                main_table(),
                width="100%",
            ),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        )
    return my_child
