import os

import reflex as rx
# Load environment variables from .env file
from dotenv import load_dotenv
from supabase import create_client, Client

import buildcheck.views.employee_upload as em
from buildcheck.views.admin_dashboard import am_dashboard
from buildcheck.views.employee_view import employee_view
from buildcheck.views.reviewer_assignment import rv_assignment
from . import views

load_dotenv()

# Fetch Supabase credentials from environment variables
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
# Create the Supabase client
supabase_client: Client = create_client(supabase_url, supabase_key)

class State(rx.State):
    is_new_account: bool = False
    name: str = ""
    badge_number: str = ""
    email: str = ""
    password: str = ""
    role: str = "employee"  # Default role
    roles: list[str] = ["admin", "employee", "reviewer"]

    def toggle_account_mode(self):
        self.is_new_account = not self.is_new_account

    @rx.event
    def set_role(self, value: str):
        self.role = value

    @rx.event
    def submit(self):
        if self.is_new_account:
            try:
                response = supabase_client.table("users").insert({
                    "name": self.name,
                    "badge_number": self.badge_number,
                    "email": self.email,
                    "password": self.password,
                    "role": self.role
                }).execute()
                if response.data:
                    print(f"Account created for: {self.name}, {self.badge_number}, {self.email}, {self.role}")
                    return rx.toast.success("Account created successfully!")
                else:
                    return rx.toast.error("Access denied. Please make sure you filled all required data.")
            except Exception as e:
                print(e)
                return rx.toast.error("An error occurred during account creation.")
        else:
            # Login: check if user exists in Supabase
            try:
                response = supabase_client.table("users").select("*").eq("email", self.email).eq("password", self.password).single().execute()
                if response.data:
                    print(f"Login successful for: {response.data['name']}")
                    return rx.redirect("/validation")
                else:
                    return rx.toast.error("Login failed. Please check your email and password.")
            except Exception as e:
                print(e)
                return rx.toast.error("An error occurred during login.")

config = rx.Config(
    app_name="buildcheck",
    show_built_with_reflex=False,
    use_single_port=True,
)

def index() -> rx.Component:
    # BuildCheck Login / Signup Page
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.center(
            rx.vstack(
                rx.image(
                    src="/logo.png",
                    alt="ARCH Logo",
                    box_size="80px",
                    margin_bottom="4",
                ),
                rx.text(
                    "Welcome! Please log in or create a new account.",
                    size="4",
                ),
                rx.cond(
                    State.is_new_account,
                    rx.vstack(
                        rx.input(
                            placeholder="Name",
                            value=State.name,
                            on_change=State.set_name,
                        ),
                        rx.input(
                            placeholder="Badge Number",
                            value=State.badge_number,
                            on_change=State.set_badge_number,
                        ),
                        rx.input(
                            placeholder="Email",
                            type="email",
                            value=State.email,
                            on_change=State.set_email,
                        ),
                        rx.input(
                            placeholder="Password",
                            type="password",
                            value=State.password,
                            on_change=State.set_password,
                        ),
                        rx.select(
                            State.roles,
                            value=State.role,
                            on_change=State.set_role,
                            placeholder="Select Role",
                        ),
                        rx.button(
                            "Create Account",
                            on_click=State.submit,
                            width="100%",
                        ),
                        rx.button(
                            "Already have an account? Log in",
                            variant="ghost",
                            on_click=State.toggle_account_mode,
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.input(
                            placeholder="Email",
                            type="email",
                            value=State.email,
                            on_change=State.set_email,
                        ),
                        rx.input(
                            placeholder="Password",
                            type="password",
                            value=State.password,
                            on_change=State.set_password,
                        ),
                        rx.button(
                            "Log In",
                            on_click=State.submit,
                            width="100%",
                        ),
                        rx.button(
                            "New user? Create an account",
                            variant="ghost",
                            on_click=State.toggle_account_mode,
                        ),
                        spacing="3",
                        width="100%",
                    ),
                ),
                spacing="6",
                width="350px",
                padding="6",
                border_radius="lg",
                box_shadow="lg",
                bg="whiteAlpha.900",
            ),
            min_height="90vh",
        ),
    )

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        # accent_color="grass"
    )
)

app.add_page(index, route="/", title="Login", description="Login or create an account")
app.add_page(views.validation_page, route="/validation")
app.add_page(views.employee_blueprint, route="/blueprint-pending")
app.add_page(views.employee_notifications, route="/employee-notifications")
app.add_page(views.admin_notifications, route="/admin-notifications")
app.add_page(views.reviewer_notifications, route="/reviewer-notifications")
app.add_page(em.upload_page, title="Employee Dashboard", description="This page is where the employee can view their case.")
app.add_page(rv_assignment, title="Blueprint Assignment")
app.add_page(employee_view, route="/employee_view", title="Employee View")
app.add_page(views.admin_assignments, route="/admin_assignments", title="Admin Assignments")
app.add_page(am_dashboard, route="/admin-dashboard", title="Admin Dashboard")