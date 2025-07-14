import reflex as rx

def stat_card(title: str, statistic, icon_name: str, color: str = "blue", subtitle: str = "") -> rx.Component:
    # statistic must be an rx.Var
    def card_title(title: str, icon_name: str, color: str) -> rx.Component:
        return rx.hstack(
            rx.text(title, font_weight="bold"),
            rx.icon(
                icon_name,
                color=color,
            ),
            spacing="2",
            align="center",
            justify="between",
            width="100%",
        )

    return rx.card(
        rx.vstack(
            card_title(title, icon_name, color),
            rx.text(statistic, font_size="2.5em", font_weight="bold", color=color),
            rx.text(subtitle, color="gray"),
        ),
        size="3",
        width="100%",
        max_width="22rem",
        min_width="2rem"
    )