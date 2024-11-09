from fastapi import FastAPI, HTTPException
from src.supabase_client import TrainingWeek, get_training_week

app = FastAPI()


@app.get("/training_week/{athlete_id}", response_model=TrainingWeek)
async def training_week_endpoint(athlete_id: int):
    """
    Retrieve the most recent training_week row by athlete_id.
    """
    try:
        return get_training_week(athlete_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
