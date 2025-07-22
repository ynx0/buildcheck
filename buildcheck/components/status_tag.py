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

def freq_tag(freq: rx.Var[str]) -> rx.Component:

    return rx.badge(
        freq,
        color_scheme=rx.match(
            freq,
            ("high", "red",),
            ("medium", "yellow",),
            ("low", "blue"),
            "gray"
        ),
        variant="soft",
        text_transform="capitalize",
    )


