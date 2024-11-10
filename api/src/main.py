import logging

from fastapi import Depends, FastAPI, HTTPException
from src import supabase_client
from src.auth_manager import validate_user
from src.types.training_week import TrainingWeek
from src.types.user import UserRow

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@app.get("/training_week/", response_model=TrainingWeek)
async def training_week(user: UserRow = Depends(validate_user)):
    """
    Retrieve the most recent training_week row by athlete_id
    curl -X GET "http://trackflow-alb-499532887.us-east-1.elb.amazonaws.com/training_week/" \
    -H "Authorization: Bearer YOUR_JWT_TOKEN"

    :param athlete_id: The athlete_id to retrieve the training_week for
    :return: The most recent training_week row for the athlete
    """
    try:
        return supabase_client.get_training_week(user.athlete_id)
    except ValueError as e:
        logger.error(f"Error retrieving training week: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
