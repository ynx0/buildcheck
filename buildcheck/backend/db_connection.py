# import os
# from supabase import create_client, Client
# from dotenv import load_dotenv
# import logging

# # Load environment variables from .env
# load_dotenv()

# # Internal variable to store the singleton client instance
# _supabase_client: Client = None

# def get_supabase_client() -> Client:
#     global _supabase_client
#     if _supabase_client is None:
#         supabase_url = os.environ.get("SUPABASE_URL")
#         supabase_key = os.environ.get("SUPABASE_KEY")

#         if not supabase_url or not supabase_key:
#             logging.error("SUPABASE_URL or SUPABASE_KEY is missing in .env")
#             raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing in .env")

#         _supabase_client = create_client(supabase_url, supabase_key)
#         logging.info("Supabase client created successfully.")

#     return _supabase_client

# # This function is safe to add. Only used when called explicitly.
# def get_guideline_violations(blueprint_id: int):
#     client = get_supabase_client()
#     if not isinstance(blueprint_id, int):
#         logging.error(f"Invalid blueprint_id: {blueprint_id}")
#         raise ValueError("blueprint_id must be an integer")
#     query = f"""
#     SELECT 
#       g.category,
#       v.severity AS status,
#       v.description AS details
#     FROM blueprints b
#     JOIN reviews r ON r.blueprint_id = b.id
#     JOIN violations v ON v.review_id = r.id
#     JOIN guidelines g ON g.code = v.guideline_code
#     WHERE b.id = {blueprint_id};
#     """
#     try:
#         response = client.rpc("exec_sql", {"sql": query})
#         if hasattr(response, 'error') and response.error:
#             logging.error(f"Supabase RPC error: {response.error}")
#             return None
#         logging.info(f"Guideline violations fetched for blueprint_id {blueprint_id}")
#         return response
#     except Exception as e:
#         logging.error(f"Error fetching guideline violations: {e}")
#         return None

# # Example: Add alt text to images and title to buttons in your UI code
# # For images:
# # rx.image(src="/logo.png", alt="ARCH Logo", box_size="80px", margin_bottom="4")
# # For buttons:
# # rx.button("View Blueprint", color_scheme="blue", title="View selected blueprint", ...)