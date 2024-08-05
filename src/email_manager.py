import os
import uuid
from typing import Dict

import sib_api_v3_sdk
from dotenv import load_dotenv

from src import constants
from src.types.training_week import TrainingWeek

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key["api-key"] = os.environ["EMAIL_API_KEY"]

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)


def training_week_to_html(training_week: TrainingWeek) -> str:
    """
    Convert a TrainingWeek object to HTML content for email

    :param training_week: TrainingWeek object
    :return: HTML content for email
    """
    uid = str(uuid.uuid4())
    html_content = constants.training_week_html_base
    for day, session in training_week.dict().items():
        html_content += f"""
                    <li>
                        <strong>{day.capitalize()}</strong>
                        <span>{session['session_type'].value} {session['distance']} miles</span><br>
                        <span>Notes: {session['notes']}</span>
                    </li>
        """
    html_content += f"""
                </ul>
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
