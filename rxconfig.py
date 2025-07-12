import reflex as rx

config = rx.Config(
    app_name="buildcheck",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.SitemapPlugin(),
    ],
)
