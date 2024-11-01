import base64
import os
import time

import httpx
import jwt
from dotenv import load_dotenv

load_dotenv()


def generate_jwt_token(key_id: str, team_id: str, private_key: str) -> str:
    """
    Generate JWT token for APNs authentication.

    :param key_id: Apple Key ID
    :param team_id: Apple Team ID
    :param private_key: Contents of the .p8 file
    :return: JWT token as a string
    """
    headers = {"alg": "ES256", "kid": key_id}
    payload = {"iss": team_id, "iat": time.time()}
    return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)


def send_push_notification(
    device_token: str, payload: dict, auth_token: str, use_sandbox: bool = False
) -> None:
    """
    Send a push notification to a device token.

    Args:
        device_token: User's device token
        payload: Notification payload
        auth_token: APNs JWT token
        use_sandbox: If True, uses sandbox environment
    """
    base_url = "api.sandbox.push.apple.com" if use_sandbox else "api.push.apple.com"
    # URL encode the device token and ensure no spaces
    clean_token = device_token.strip().replace(" ", "")
    url = f"https://{base_url}/3/device/{clean_token}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "apns-topic": "voynow.mobile",
        "content-type": "application/json",
    }

    try:
        client = httpx.Client(http2=True, verify=True, timeout=30.0)
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Notification sent successfully")
        client.close()

    except httpx.RequestError as e:
        print(f"Connection error: {e}")
        raise
    except httpx.HTTPStatusError as e:
        error_payload = response.json() if response.content else "No error details"
        print(f"APNs error: {response.status_code}, {error_payload}")
        raise ValueError(f"APNs rejected the request: {error_payload}")


auth_token = generate_jwt_token(
    key_id=os.environ["APN_KEY_ID"],
    team_id=os.environ["APN_TEAM_ID"],
    private_key=base64.b64decode(os.environ["APN_PRIVATE_KEY"]).decode(),
)

device_token = "..."
payload = {
    "aps": {
        "alert": {"title": "Hello", "body": "This is a test notification"},
        "sound": "default",
    }
}
send_push_notification(device_token, payload, auth_token)
