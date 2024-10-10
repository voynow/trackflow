import logging
import os
import traceback
import uuid

from src import auth_manager, frontend_router, update_pipeline, webhook_router
from src.email_manager import send_alert_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def strategy_router(event: dict, invocation_id: str) -> dict:
    """
    Route the event to the appropriate handler based on the event type.

    :param event: The event dictionary containing event data
    :param invocation_id: The unique identifier for the invocation
    :return: {"success": bool, other_metadata: dict} where the error key is
             only present if success is False
    """

    # Will fail on bad authenticate_with_code
    if event.get("email") and event.get("code"):
        return auth_manager.signup(
            email=event["email"],
            code=event["code"],
        )

    # Will fail on bad authenticate_with_code
    elif event.get("code"):
        user_auth = auth_manager.authenticate_with_code(event["code"])
        return {"success": True, "jwt_token": user_auth.jwt_token}

    elif event.get("jwt_token") and event.get("method"):
        return frontend_router.handle_request(
            jwt_token=event["jwt_token"],
            method=event["method"],
            payload=event.get("payload"),
        )

    elif (
        event.get("subscription_id")
        and event.get("aspect_type")
        and event.get("object_type")
        and event.get("object_id")
        and event.get("owner_id")
    ):
        return webhook_router.handle_request(event, invocation_id)

    # This will only run if triggered by NIGHTLY_EMAIL_TRIGGER_ARN
    elif (
        event.get("resources")
        and event.get("resources")[0] == os.environ["NIGHTLY_EMAIL_TRIGGER_ARN"]
    ):
        return update_pipeline.nightly_trigger_orchestrator(invocation_id)

    elif event.get("trigger_test_key") == os.environ["TRIGGER_TEST_KEY"]:
        return update_pipeline.integration_test_executor(invocation_id)
    else:
        return {"success": False, "error": f"Unknown event type: {event}"}


def lambda_handler(event, context):
    """
    Main entry point, responsible for logging and error handling, producing
    email alerts on errors and failures

    :param event: lambda event
    :param context: lambda context
    :return: dict with {"success": bool}
    """
    invocation_id = str(uuid.uuid4())
    logger.info(f"{invocation_id=} | {event=} | {context=}")

    try:
        response = strategy_router(event, invocation_id)
    except Exception as e:
        response = {
            "success": False,
            "error": f"{invocation_id=} | Error in lambda_handler: {str(e)}\nTraceback: {traceback.format_exc()}",
        }

    # Ensure response is a dictionary
    if type(response) is not dict:
        response = {"success": False, "error": f"Unknown response type: {response}"}

    # Ensure response has success key
    if "success" not in response:
        response = {"success": False, "error": f"Unknown response: {response}"}

    # Send alert on any and all errors/failures
    if response["success"]:
        logger.info(f"{invocation_id=} | {response=}")
        return response
    else:
        logger.error(f"{invocation_id=} | Error in lambda_handler: {response['error']}")
        send_alert_email(
            subject="TrackFlow Alert: Error in lambda_handler",
            text_content=f"{invocation_id=} | {response['error']}",
        )
        return {"success": False}
