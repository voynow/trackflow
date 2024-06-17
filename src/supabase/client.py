import os

from supabase import Client, create_client

from src.supabase.models import UserAuthRow


def init() -> Client:
    """ """
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


client = init()


def upsert_user_auth(user_auth_row: UserAuthRow):
    table = client.table("user_auth")
    data, _ = table.upsert(user_auth_row).execute()
    return {"status": "ok", "data": data}
