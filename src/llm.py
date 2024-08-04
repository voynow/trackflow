import json
from typing import Type
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()


def get_completion_json(
    message: str,
    response_model: Type[BaseModel],
    model: str = "gpt-4o",
    max_retries: int = 3,
) -> BaseModel:

    response_model_content = f"Your json response must follow the following: {response_model.schema()=}"

    retries = 0
    while retries < max_retries:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant designed to output JSON."
                    + response_model_content,
                },
                {"role": "user", "content": message},
            ],
            response_format={"type": "json_object"},
        )
        response_content = json.loads(response.choices[0].message.content)

        try:
            return response_model(**response_content)
        except Exception as e:
            retries += 1
            if retries < max_retries:
                continue
            else:
                raise Exception(
                    f"Failed to get a valid response after {max_retries} attempts: {response_content=}, {e=}"
                )
