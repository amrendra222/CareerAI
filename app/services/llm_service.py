from openai import OpenAI

from app.config import settings


client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def generate_response(prompt: str) -> str:

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are CareerAI, an expert AI interviewer "
                    "and career intelligence assistant."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3,

        max_completion_tokens=4096,

        reasoning_effort="low",

        stream=False
    )

    message = response.choices[0].message

    content = message.content

    if content:
        return content.strip()

    # GPT-OSS can expose reasoning separately.
    # We should never use reasoning as the final answer.
    return ""