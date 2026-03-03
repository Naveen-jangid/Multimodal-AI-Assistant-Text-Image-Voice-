"""LLM integration using OpenAI GPT-4o."""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a helpful, knowledgeable AI assistant with multimodal capabilities. "
    "You can analyze text, images, and transcribed voice input to provide accurate, "
    "concise, and useful responses. When analyzing food images, provide detailed "
    "nutritional information. Be friendly and informative."
)


def get_text_response(user_message: str, conversation_history: list = None) -> str:
    """Generate a response for a plain text query."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return response.choices[0].message.content


def get_vision_response(user_message: str, image_base64: str, mime_type: str = "image/jpeg") -> str:
    """Generate a response for an image + optional text query."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_base64}",
                        "detail": "high",
                    },
                },
                {"type": "text", "text": user_message or "Describe this image in detail."},
            ],
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return response.choices[0].message.content
