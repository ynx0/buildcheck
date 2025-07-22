import reflex as rx

class UserState(rx.State):
    #Global user state management.
    
    # User information
    user_id: str = ""
    name: str = ""
    nameIntials: str = ""
    email: str = ""
    role: str = ""
    badge_number: str = ""

    def set_user(self, user_data: dict):
        #Set user information from login response.

        self.user_id = user_data["id"]
        self.name = user_data["name"]
        self.email = user_data["email"]
        self.role = user_data["role"]
        self.badge_number = user_data["badge_number"]
        self.nameIntials = "".join(part[0].upper() for part in self.name.split() if part)  # Update initials after setting name 
    def clear_user(self):
        #Clear user information on logout.
        self.user_id = ""
        self.name = ""
        self.email = ""
        self.role = ""
        self.badge_number = ""
    
    @rx.event
    async def handle_logout(self):
        self.clear_user()
        return rx.redirect("/")  # Redirect to login page