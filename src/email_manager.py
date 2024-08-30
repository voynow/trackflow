import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import sib_api_v3_sdk
from dotenv import load_dotenv
from jinja2 import Template
from pydantic import BaseModel
from urllib3.exceptions import ProtocolError

from src.types.mid_week_analysis import MidWeekAnalysis
from src.types.training_week import (
    TrainingWeekWithCoaching,
    TrainingWeekWithPlanning,
)

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = os.environ["EMAIL_API_KEY"]

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


class EmailSession(BaseModel):
    day: str
    session_type: str
    distance: float
    notes: str


def get_email_style() -> str:
    """Returns the CSS styling for the email."""
    return """
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
            background-color: #5A86D5;
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }

        .header h1 {
            margin: 0;
            font-size: 24px;
        }

        .content {
            margin-top: 20px;
        }

        .content ul {
            list-style-type: none;
            padding-left: 20px;
            padding-right: 20px;
        }

        .content li {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 5px solid #5A86D5;
            border-radius: 5px;
            color: #333;
            margin-bottom: 5px;
        }

        .content li.completed {
            border-left-color: #28a745;
            color: #333;
        }

        .miles-summary {
            background-color: #5A86D5;
            padding: 20px 30px;
            margin-top: 20px;
            border-radius: 10px;
            text-align: center;
            color: #ffffff;
            margin-bottom: 20px;
        }
        .total-miles-planned {
            background-color: #4671c1;
            padding: 20px 30px;
            margin-top: 20px;
            border-radius: 10px;
            text-align: center;
            color: #ffffff;
            margin-bottom: 20px;
        }
        
        .miles-label {
            font-weight: bold;
            font-size: 24px;
            color: #ffffff;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 15px;
            overflow: hidden;
            margin-top: 10px;
        }

        .progress {
            height: 100%;
            background-color: #4CAF50;
            color: #ffffff;
            font-weight: bold;
        }

        .footer {
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 9px;
            color: #777;
        }
        """


def generate_html_template(
    content: str, header: str, summary: Optional[str] = None
) -> str:
    """Generates the base HTML template with provided content."""
    template_str = """
    <html>
    <head><style>{{ style }}</style></head>
    <body>
        <div class="container">
            <div class="header"><h1>{{ header }}</h1></div>
            <div class="content">{{ content | safe }}</div>
            {% if summary %}<div class="miles-summary">{{ summary | safe }}</div>{% endif %}
            <div class="footer">
                <p style="font-size: 15px; color: #777">TrackFlow🏃‍♂️🎯 powered by the Strava API and OpenAI</p>
                <p>{{ uid }}</p>
            </div>
        </div>
    </body>
    </html>
    """
    template = Template(template_str)
    return template.render(
        style=get_email_style(),
        content=content,
        header=header,
        summary=summary,
        uid=str(uuid4()),
    )


def generate_session_list(sessions: List[EmailSession], session_type: str = "") -> str:
    """Generates an HTML list of sessions."""
    return "".join(
        f"""
    <li class="{session_type}">
        <strong>{session.day}</strong> <span>{session.distance} miles</span><br>
        <span>{session.notes}</span>
    </li>
    """
        for session in sessions
    )


def training_week_update_to_html(
    mid_week_analysis: MidWeekAnalysis,
    training_week_update_with_planning: TrainingWeekWithPlanning,
) -> str:
    """Generates HTML for training week update."""
    completed_sessions = [
        EmailSession(
            day=datetime.strptime(activity.date, "%A, %B %d, %Y")
            .strftime("%a")
            .capitalize(),
            session_type="completed",
            distance=activity.distance_in_miles,
            notes=f"Pace: {activity.pace_minutes_per_mile} min/mile, Elevation: {activity.elevation_gain_in_feet} feet",
        )
        for activity in mid_week_analysis.activities
    ]

    upcoming_sessions = [
        EmailSession(
            day=session.day.capitalize(),
            session_type=session.session_type.value,
            distance=session.distance,
            notes=session.notes,
        )
        for session in training_week_update_with_planning.training_week
    ]

    content = f"<ul>{generate_session_list(completed_sessions, 'completed')}{generate_session_list(upcoming_sessions, 'upcoming')}</ul>"

    progress_percentage = (
        (mid_week_analysis.miles_ran / mid_week_analysis.miles_target) * 100
        if mid_week_analysis.miles_target > 0
        else 0
    )
    miles_ran = round(mid_week_analysis.miles_ran)
    miles_target = round(mid_week_analysis.miles_target)
    progress = round(progress_percentage)
    summary = f"""
    <span class="miles-label">Completed {miles_ran} out of {miles_target} miles</span>
    <div class="progress-bar">
        <div class="progress" style="width: {progress_percentage}%;">{progress}%</div>
    </div>
    """

    return generate_html_template(
        content=content,
        header="Updated Training Schedule",
        summary=summary,
    )


def new_training_week_to_html(
    training_week_with_coaching: TrainingWeekWithCoaching,
) -> str:
    """Generates HTML for training week."""
    upcoming_sessions = [
        EmailSession(
            day=session.day.capitalize(),
            session_type=session.session_type.value,
            distance=session.distance,
            notes=session.notes,
        )
        for session in training_week_with_coaching.training_week
    ]
    content = f"<ul>{generate_session_list(upcoming_sessions)}</ul>"
    summary = f"""
    <h2>Coach's Recommendation</h2>
    <p>{training_week_with_coaching.weekly_mileage_target}</p>
    <div class='total-miles-planned'>
        <span class='miles-label'>Total Miles Planned: {training_week_with_coaching.total_weekly_mileage}</span>
    </div>
    """

    return generate_html_template(
        content=content,
        header="Your Training Schedule",
        summary=summary,
    )


def send_email(
    subject: str,
    html_content: str,
    to: Dict[str, str],
    sender: Dict[str, str] = {
        "name": "Jamie Voynow",
        "email": "voynowtestaddress@gmail.com",
    },
) -> sib_api_v3_sdk.CreateSmtpEmail:
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[to], html_content=html_content, sender=sender, subject=subject
    )
    try:
        return api_instance.send_transac_email(send_smtp_email)
    except ProtocolError:
        return api_instance.send_transac_email(send_smtp_email)


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


def mock_send_email(
    subject: str,
    html_content: str,
    to: Dict[str, str],
    sender: Dict[str, str] = {
        "name": "Jamie Voynow",
        "email": "voynowtestaddress@gmail.com",
    },
) -> sib_api_v3_sdk.CreateSmtpEmail:
    """Mock version of send_email for testing"""
    return sib_api_v3_sdk.CreateSmtpEmail(message_id="12345")
