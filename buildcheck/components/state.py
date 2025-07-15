# from urllib import response
# import reflex as rx
# from typing import List
# from buildcheck.backend.db_connection import get_supabase_client

# # State to manage selected blueprint and dropdown options
# class BlueprintState(rx.State):
#     selected: str = ""
#     blueprint_items: list[dict] = []

#     def load_blueprints(self):
#         supabase = get_supabase_client()
#         response = supabase.table("blueprints").select("id, title").execute()
        
#         print("Supabase response:", response.data)  # Debug line

#         if response.data:
#             self.blueprint_items = [
#                 {"label": row["title"], "value": str(row["id"])}
#                 for row in response.data
#             ]

#             print("Loaded items:", self.blueprint_items)


#         else:
#             print(" No blueprints found.")

#             self.blueprint_items = []

#             print("Received blueprints:", response.data)

#     def set_blueprint(self, value: str):
#         self.selected = value
#         if value:
#             self.load_guidelines(int(value))
#         else:
#             GuidelinesState.guidelines = []

# # State to manage guideline violations for the selected blueprint
# class GuidelinesState(rx.State):
#     guidelines: list[dict] = []

#     def load_guidelines(self, blueprint_id: int):
#         """Call the RPC function to get guideline violations for a blueprint."""
#         supabase = get_supabase_client()
#         response = supabase.rpc("get_guideline_violations", {
#             "blueprint_id": blueprint_id
#         }).execute()

#         print(f"RPC response for blueprint_id {blueprint_id}: {response.data}")  # Debug line

#         if response.data:
#             self.guidelines = [
#                 {
#                     "category": row["category"],
#                     "status": row["status"],
#                     "details": row["details"]
#                 }
#                 for row in response.data
#             ]
#             print(f"Loaded guidelines: {self.guidelines}")  # Debug line
#         else:
#             self.guidelines = []
#             print("No guidelines found for this blueprint.")  # Debug line

#     def load_selected_guidelines(self, _):
#         if BlueprintState.selected:
#             self.load_guidelines(int(BlueprintState.selected))
#         else:
#             self.guidelines = []
