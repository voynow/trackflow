import datetime
import os
from typing import Dict

from dotenv import load_dotenv
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


def upsert_user_auth(user_auth_row: UserAuthRow) -> Dict:
    """
    Convert UserAuthRow to a dictionary, ensure json serializable expires_at,
    and upsert into user_auth table

    :param user_auth_row: UserAuthRow
    :return: Dict
    """
    user_auth_dict = user_auth_row.dict()
    user_auth_dict["expires_at"] = (
        user_auth_dict["expires_at"].isoformat()
        if isinstance(user_auth_dict["expires_at"], datetime.datetime)
        else user_auth_dict["expires_at"]
    )

    table = client.table("user_auth")
    data, _ = table.upsert(user_auth_dict).execute()

    return {"status": "ok", "data": data}
