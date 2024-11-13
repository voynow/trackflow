from src import auth_manager, supabase_client
from src.types.webhook import StravaEvent

# from src.training_week import update_training_week
# from src.types.exe_type import ExeType


def handle_activity_create(event: StravaEvent) -> dict:
    """
    Handle the creation of a Strava activity

    :param event: Strava webhook event
    """
    pass
    # user = supabase_client.get_user(event.owner_id)
    # strava_client = auth_manager.get_strava_client(user.athlete_id)
    # activity = strava_client.get_activity(event.object_id)

    # if activity.sport_type == "Run":
    #     return update_training_week(
    #         user=user,
    #         exe_type=ExeType.MID_WEEK,
    #     )
    # return {
    #     "success": False,
    #     "error": f"Unsupported activity type: {activity.sport_type}",
    # }


def maybe_process_strava_event(event: StravaEvent) -> dict:
    """
    Process the Strava webhook event. Perform any updates based on the event data.
    Strava Event: subscription_id=2****3 aspect_type='create' object_type='activity' object_id=1*********4 owner_id=9******6 event_time=1731515741 updates={}
    Strava Event: subscription_id=2****3 aspect_type='update' object_type='activity' object_id=1*********9 owner_id=9******6 event_time=1731515699 updates={'title': 'Best running weather ❄️'}

    :param event: Strava webhook event
    :return: Success status and error message if any
    """
    if event.aspect_type == "create":
        return handle_activity_create(event)
    else:
        return {
            "success": False,
            "error": f"Unsupported event type: {event.aspect_type}",
        }
