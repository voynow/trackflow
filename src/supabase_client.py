import datetime
import os
from typing import Dict

from dotenv import load_dotenv
from postgrest.base_request_builder import APIResponse
from supabase import Client, create_client
from supabase_models import UserAuthRow

load_dotenv()


def init() -> Client:
    """ """
    url: str = os.environ["SUPABASE_URL"]
    key: str = os.environ["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase


client = init()


def upsert_user_auth(user_auth_row: UserAuthRow) -> APIResponse:
    """
    Convert UserAuthRow to a dictionary, ensure json serializable expires_at,
    and upsert into user_auth table handling duplicates on athlete_id

    :param user_auth_row: A dictionary representation of UserAuthRow
    :return: APIResponse
    """
    user_auth_row = user_auth_row.dict()
    if isinstance(user_auth_row["expires_at"], datetime.datetime):
        user_auth_row["expires_at"] = user_auth_row["expires_at"].isoformat()

    table = client.table("user_auth")
    response = table.upsert(user_auth_row, on_conflict="athlete_id").execute()

    return response
