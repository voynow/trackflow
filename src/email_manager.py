import os
import uuid
from typing import Dict

import sib_api_v3_sdk
from dotenv import load_dotenv

from src.types.training_week_with_coaching import TrainingWeekWithCoaching

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = os.environ["EMAIL_API_KEY"]

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


def training_week_to_html(training_week_with_coaching: TrainingWeekWithCoaching) -> str:
    """
    Convert a TrainingWeek object to HTML content for email

    :param training_week: TrainingWeek object
    :return: HTML content for email
    """
    uid = str(uuid.uuid4())
    total_miles = sum(
        [
            session["distance"]
            for session in training_week_with_coaching.training_week.dict().values()
            if isinstance(session, dict)
        ]
    )

    html_content = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            .header {
                background-color: #6495ED;
                color: #ffffff;
                text-align: center;
                padding: 20px;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .content {
                padding: 20px;
            }
            .content h2 {
                color: #6495ED;
                font-size: 20px;
                margin-bottom: 10px;
            }
            .content ul {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            .content li {
                background-color: #f9f9f9;
                margin-bottom: 10px;
                padding: 15px;
                border-left: 5px solid #6495ED;
                border-radius: 5px;
                color: #333;
            }
            .content li strong {
                display: block;
                font-size: 16px;
                margin-bottom: 5px;
                color: #333;
            }
            .review-section, .mileage-target-section {
                margin-top: 30px;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .footer {
                background-color: #f1f1f1;
                text-align: center;
                padding: 10px;
                font-size: 9px;
                color: #777;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Your Training Schedule</h1>
            </div>
            <div class="content">
                <h2>Get pumped for this week's training.</h2>
                <ul>
    """
    for day, session in training_week_with_coaching.training_week.dict().items():
        if isinstance(session, dict):  # Skip non-session fields
            html_content += f"""
                    <li>
                        <strong>{day.capitalize()}</strong>
                        <span>{session['session_type'].value} {session['distance']} miles</span><br>
                        <span>Notes: {session['notes']}</span>
                    </li>
            """
    html_content += f"""
                </ul>
                <h2>Total Miles Planned: {total_miles}</h2>
                <div class="review-section">
                    <h2>Coach's Review</h2>
                    <p>{training_week_with_coaching.typical_week_training_review}</p>
                </div>
                <div class="mileage-target-section">
                    <h2>Weekly Mileage Target</h2>
                    <p>{training_week_with_coaching.weekly_mileage_target}</p>
                </div>
            </div>
            <div class="footer">
                <p style="font-size: 15px; color: #777;">Powered by the Strava API and OpenAI</p>
                <p>{uid}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


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
