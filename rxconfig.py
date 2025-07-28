import reflex as rx

config = rx.Config(
    app_name="buildcheck",
    plugins=[
        rx.plugins.TailwindV4Plugin(),
    ],
    disable_plugins=['reflex.plugins.sitemap.SitemapPlugin'],
)
