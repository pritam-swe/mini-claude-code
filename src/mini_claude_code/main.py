from google import genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


client = genai.Client(api_key=GEMINI_API_KEY)

response_1 = client.models.generate_content(
    model='gemini-3.1-flash-lite',
    contents='Explain what an AI agent is in one sentence.',
)


def interact():
    interaction = client.interactions.create(
    model="gemini-3.1-flash-lite",
    input="Explain how AI works in a few words"
    )
    client.close()
    return interaction.output_text

print(interact())

