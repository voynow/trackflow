import logging
import traceback
import uuid

from src.email_manager import send_alert_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def strategy_router(event: dict) -> dict:
    """
    Route the event to the appropriate handler based on the event type

    This API is public but each method is protected in some way

    :param event: The event dictionary containing event data
    :param invocation_id: The unique identifier for the invocation
    :return: {"success": bool, other_metadata: dict} where the error key is
             only present if success is False
    """
    return {"success": False, "error": f"Could not route event: {event}"}


def lambda_handler(event, context):
    """
    Main entry point, responsible for logging and error handling, producing
    email alerts on errors and failures

    :param event: lambda event
    :param context: lambda context
    :return: dict with {"success": bool}
    """
    invocation_id = str(uuid.uuid4())
    logger.info(f"{invocation_id=} | {event=}")

    try:
        response = strategy_router(event)
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
