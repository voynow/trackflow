import json
from typing import Dict, List, Optional, Type

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from pydantic import BaseModel

load_dotenv()
client = OpenAI()


def get_completion(
    messages: List[ChatCompletionMessage],
    model: str = "gpt-4o-2024-08-06",
    response_format: Optional[Dict] = None,
):
    response = client.chat.completions.create(
        model=model, messages=messages, response_format=response_format
    )
    return response.choices[0].message.content


def get_completion_json(
    message: str,
    response_model: Type[BaseModel],
    model: str = "gpt-4o-2024-08-06",
) -> BaseModel:

    response_model_content = (
        f"Your json response must follow the following: {response_model.schema()=}"
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant designed to output JSON."
            + response_model_content,
        },
        {"role": "user", "content": message},
    ]

    response = json.loads(
        get_completion(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
        )
    )

    try:
        return response_model(**response)
    except Exception as e:
        raise Exception(f"Failed to get a valid response: {response=}, {e=}")
