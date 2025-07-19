import reflex as rx
from datetime import datetime, timedelta
from random import randint
import calendar

from buildcheck.components.footer import footer
from buildcheck.components.navbar import navbar
from buildcheck.components.stat_card import stat_card
from buildcheck.components.status_tag import freq_tag

HTML2CANVAS_PRO_SRC="https://unpkg.com/html2canvas-pro@1.5.11/dist/html2canvas-pro.js"
months = list(map(lambda x: x[:3], calendar.month_name[1:]))

class AdminDashState(rx.State):
    total_reviewers: int = 1
    bp_review: int = 15
    bp_approved: int = 12
    review_time_avg_days: float = 2.3
    successes: list[dict] = []


    @rx.event
    def no_op(self):
        # needed to suppress _call_script no callback error
        pass

    async def randomize_successes(self):
        # yield rx.call_script("alert('hi')")
        if self.successes:
            return


        self.successes = [
            {
                "month": months[i],
                "success_count": randint(25, 100)
            } for i in range(12)
        ]



def pretty_time_diff(past, now=None):
    if now is None:
        now = datetime.now()
    diff = now - past
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} seconds ago"
    elif seconds < 3600:
        minutes = round(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = round(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = round(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"



def cards() -> rx.Component:
    return rx.flex(
        stat_card(
            "Total Reviewers",
            AdminDashState.total_reviewers,
            "users",
            "blue",
            "Active reviewers in the system"
        ),
        stat_card(
            "Blueprints under review",
            AdminDashState.bp_review,
            "file-clock",
            subtitle="Currently being processed by reviewers"
        ),
        stat_card(
            "Approved Blueprints",
            AdminDashState.bp_approved,
            "circle-check-big",
            subtitle="Successfully approved this month"
        ),
        stat_card(
            "Average Review Time",
            AdminDashState.review_time_avg_days,
            "timer",
            "green",
            subtitle="Average time for blueprint review"
        ),
        wrap="wrap",
        size="3",
        width="100%",
        spacing="5",
    )



def validation_trends() -> rx.Component:
    def progress_header() -> rx.Component:
        return rx.vstack(
            rx.text("Validation Success Trends", size="3", font_weight="bold"),
            rx.text("Monthly overview", size="2", color="gray"),
            spacing="1"
        )

    return rx.card(
        rx.vstack(
            progress_header(),
            rx.spacer(),
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.bar(
                    data_key="success_count",
                    stroke=rx.color("blue", 9),
                    fill=rx.color("blue", 7),
                ),
                rx.recharts.x_axis(data_key="month", scale="auto"),
                rx.recharts.y_axis(),
                width="100%",
                data=AdminDashState.successes,
                height=250,
            )
        ),
        spacing="2"
    )



def overall_progress() -> rx.Component:

    def activity() -> rx.Component:
        return rx.vstack(
            rx.text("Overall Validation Progress", size="3", font_weight="bold"),
            rx.text("Proportion of plans successfully validated", size="2", color="gray"),
            spacing="1"
        )

    return rx.card(
        rx.vstack(
            activity(),
            rx.hstack(
                rx.heading("80%", color="blue", size="8"),
                rx.text("(987 of 1234)", color="gray"),
                align="baseline"
            ),
            rx.progress(value=80),
            rx.text(
                "Represents the proportion of plans that have successfully"
                "completed the validation process.",
                color="gray",
                size="2"
            ),
        )
    )


def recent_activity() -> rx.Component:
    activity = [
        {"id": 7890, "act": "assigned to", "recipient": "Jane Doe", "datetime": datetime.now() - timedelta(minutes=2)},
        {"id": 4382, "act": "assigned to", "recipient": "John Smith", "datetime": datetime.now() - timedelta(minutes=3)}
    ]


    def row(action) -> rx.Component:
        return rx.vstack(
            # TODO make this real
            rx.text(f"Blueprint #{action["id"]} {action["act"]} to {action["recipient"]}"),
            rx.text(str(action["datetime"]), size="1", color="gray")
        )

    return rx.card(rx.vstack(
        rx.heading("Recent Activity", size="5"),
        rx.spacer(),
        *(row(action) for action in activity),
        width="100%",
        overflow_x="auto",
        padding="1em",
        variant="surface"
    ))



def main_content1() -> rx.Component:
    return rx.grid(
        validation_trends(),
        recent_activity(),
        gap="1rem",
        grid_template_columns=[
            "2fr 1fr",
        ],
        width="100%",
    )







def common_violations() -> rx.Component:

    violations = [
        {"violation_type": "Room Size", "desc": "Living room too large", "guideline": "Section 2.3, Page 14", "freq": "high"},
        {"violation_type": "Electrical Layout", "desc": "Insufficient outlets", "guideline": "Section 2.4, Page 3", "freq": "medium"},
        {"violation_type": "Window placement", "desc": "Not enough windows", "guideline": "Section 3.4, Page 4", "freq": "low"},
    ]

    return rx.card(
        rx.vstack(
            rx.heading("Common Guideline Violations"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Violation Type", text_transform="uppercase"),
                        rx.table.column_header_cell("Description", text_transform="uppercase"),
                        rx.table.column_header_cell("Guideline Reference", text_transform="uppercase"),
                        rx.table.column_header_cell("Frequency", text_transform="uppercase"),
                    )
                ),
                rx.table.body(
                    *[
                        rx.table.row(
                            rx.table.cell(violation["violation_type"]),
                            rx.table.cell(violation["desc"]),
                            rx.table.cell(violation["guideline"]),
                            rx.table.cell(freq_tag(violation["freq"])),
                        )
                        for violation in violations
                    ]
                ),
                width="100%",
                # max_width="40em",
                overflow_x="auto",
                padding="1em",
                variant="surface"
            )
        )
    )


def main_content2() -> rx.Component:
    return rx.grid(
        overall_progress(),
        common_violations(),
        gap="1rem",
        grid_template_columns=[
            "1fr 2fr",
        ],
        width="100%",
    )


# @rx.page(route='/admin-dashboard', on_load=AdminDashState.randomize_successes)
def am_dashboard() -> rx.Component:
    return rx.vstack(
        rx.script(src=HTML2CANVAS_PRO_SRC),
        rx.script(src='/export-lib.js'),
        navbar(),
        rx.flex(
            rx.heading("Admin Dashboard", size="9"),
            rx.button("Export Report", on_click=rx.call_script("downloadPDF()", callback=AdminDashState.no_op)),
            justify="between",
            align="baseline",
            width="100%",
        ),
        cards(),
        main_content1(),
        main_content2(),
        align="start",
        spacing="3",
        padding="3",
        padding_x=["1.5em", "1.5em", "3em"],
    ), footer()