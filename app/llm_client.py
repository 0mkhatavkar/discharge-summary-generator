import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise RuntimeError("SARVAM_API_KEY not found — check your .env file")

client = SarvamAI(api_subscription_key=api_key)

def call_llm(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions(
        model="sarvam-105b",
        messages=messages,
        reasoning_effort=None,  # skip the internal "thinking" trace -- we just want the JSON
        max_tokens=2048,
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError(
            f"Sarvam returned no content (finish_reason={response.choices[0].finish_reason}). "
            "Response may have been cut off -- try raising max_tokens."
        )
    return content