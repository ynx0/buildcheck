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
        # have to fix this --> Expected field 'UserState.user_id' to receive type '<class 'str'>', but got '2' of type '<class 'int'>'.
        self.user_id = str(user_data.get("id",""))
        self.name = str(user_data.get("name",""))
        self.email = str(user_data.get("email",""))
        self.role = str(user_data.get("role",""))
        self.badge_number = str(user_data.get("badge_number", ""))
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