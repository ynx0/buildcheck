import reflex as rx

from buildcheck.components.footer import footer
from buildcheck.components.navbar import navbar

class AdminDashState(rx.State):
    total_reviewers: int = 1
    bp_review: int = 15
    bp_approved: int = 12
    review_time_avg_days: float = 2.3


# title
# cards list flex
# 2 column report , recent activity

def stat_card(title: str, statistic, icon_name: str, color: str) -> rx.Component:
    return rx.box()

def cards() -> rx.Component:
    return rx.flex(
        stat_card(
            "Total Reviewers",
            AdminDashState.total_reviewers,
            "users",
            "blue"
        ),
        stat_card("Total Reviewers", AdminDashState.total_reviewers, "users"
                                                                     "blue", "black"),
    )

def stats() -> rx.Component:
    return rx.box()

def recent_activity() -> rx.Component:
    return rx.box()

def main_content() -> rx.Component:
    return rx.flex()


@rx.page(route='/admin-dashboard')
def am_dashboard() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.heading("Admin Dashboard", size="9"),
        cards(),
        main_content(),
        footer(),
        spacing="3",
        padding="3",
        padding_x=["1.5em", "1.5em", "3em"]
    )