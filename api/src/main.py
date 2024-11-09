from fastapi import Depends, FastAPI, HTTPException
from src.auth_manager import get_current_user
from src.supabase_client import TrainingWeek, get_training_week

app = FastAPI()


@app.get("/training_week/{athlete_id}", response_model=TrainingWeek)
async def training_week_endpoint(athlete_id: int, _: dict = Depends(get_current_user)):
    """
    Retrieve the most recent training_week row by athlete_id
    curl -X GET "http://localhost:8000/training_week/{athlete_id}" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"

    :param athlete_id: The athlete_id to retrieve the training_week for
    :return: The most recent training_week row for the athlete
    """
    try:
        return get_training_week(athlete_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
