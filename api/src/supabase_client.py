from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from src.types.training_week import TrainingWeek
from supabase import Client, create_client

load_dotenv()


def init() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)


client = init()


def get_training_week(athlete_id: int) -> TrainingWeek:
    """
    Get the most recent training_week row by athlete_id.
    """
    table = client.table("training_week")
    response = (
        table.select("training_week")
        .eq("athlete_id", athlete_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    try:
        response_data = response.data[0]
        return TrainingWeek(**json.loads(response_data["training_week"]))
    except IndexError:
        raise ValueError(
            f"Could not find training_week row for athlete_id {athlete_id}"
        )
