import reflex as rx



def status_tag(status: str) -> rx.Component:
    colors = {
        "pending": "yellow",
        "approved": "green",
        "rejected": "red",
        "canceled": "gray",
    }
    return rx.badge(
        status,
        color_scheme=colors.get(status, "gray"),
        variant="soft",
        text_transform="capitalize",
        # radius="full",
        # size="3"
    )