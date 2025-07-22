import reflex as rx



def status_tag(status: rx.Var[str]) -> rx.Component:

    return rx.badge(
        status,
        color_scheme=rx.match(
            status,
            ("pending", "yellow"),
            ("approved", "green"),
            ("rejected", "red"),
            ("canceled", "gray"),
            "gray"
        ),
        variant="soft",
        text_transform="capitalize",
    )

def freq_tag(freq: str) -> rx.Component:
    colors = {
        "high": "red",
        "medium": "yellow",
        "low": "blue"
    }

    return rx.badge(
        freq,
        color_scheme=colors.get(freq, "gray"),
        variant="soft",
        text_transform="capitalize",
    )