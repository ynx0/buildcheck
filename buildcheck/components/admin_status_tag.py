import reflex as rx

def get_admin_status_tag(status: str) -> rx.Component:
    # Normalize key
    key = status.strip().lower()

    # Color mapping with lowercase keys
    colors = {
        "unassigned": "gray",
        "in review": "blue",
        "completed": "green",
    }


    return rx.badge(
        status.title(),  # Show as "In Review", etc.
        color_scheme=colors.get(key, "gray"),
        variant="soft",
        text_transform="capitalize",
    )
