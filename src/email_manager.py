import os
from typing import Dict

import sib_api_v3_sdk
from dotenv import load_dotenv

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = os.environ["EMAIL_API_KEY"]


api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


def send_email(
    subject: str,
    html_content: str,
    to: list = [{"email": "voynow99@gmail.com", "name": "Jamie Voynow"}],
    sender: Dict[str, str] = {
        "name": "Jamie Voynow",
        "email": "voynowtestaddress@gmail.com",
    },
) -> sib_api_v3_sdk.CreateSmtpEmail:
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, html_content=html_content, sender=sender, subject=subject
    )
    return api_instance.send_transac_email(send_smtp_email)
