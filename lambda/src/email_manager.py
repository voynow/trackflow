import os
from typing import Dict

import sib_api_v3_sdk
from dotenv import load_dotenv
from urllib3.exceptions import ProtocolError

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = os.environ["EMAIL_API_KEY"]

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


def send_alert_email(
    subject: str,
    text_content: str,
    to: Dict[str, str] = {
        "name": "Jamie Voynow",
        "email": "voynow99@gmail.com",
    },
    sender: Dict[str, str] = {
        "name": "Jamie Voynow",
        "email": "voynowtestaddress@gmail.com",
    },
) -> sib_api_v3_sdk.CreateSmtpEmail:
    """
    Generic template to send alerts/notifications to myself based on miscellaneous events
    """
    html_content = f"""
    <html>
    <body>
        <h1>{subject}</h1>
        <p>{text_content}</p>
    </body>
    </html>
    """
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[to], html_content=html_content, sender=sender, subject=subject
    )
    try:
        return api_instance.send_transac_email(send_smtp_email)
    except ProtocolError:
        return api_instance.send_transac_email(send_smtp_email)
