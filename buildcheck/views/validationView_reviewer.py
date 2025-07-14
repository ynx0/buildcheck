import reflex as rx
from ..components.boilerplate_stats_cards import stats_cards_group
from buildcheck.components.navbar import navbar
from buildcheck.components.footer import footer

def validation_page() -> rx.Component:
    my_child = rx.vstack(
            navbar(),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ), footer()
    return my_child
