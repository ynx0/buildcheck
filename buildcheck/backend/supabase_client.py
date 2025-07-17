import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env if using locally
load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

# Create a single, reusable Supabase client
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)