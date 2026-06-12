from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

response = client.chat.completions.create(
    model="meta/llama-4-maverick-17b-128e-instruct",
    messages=[
        {
            "role": "user",
            "content": "Are you good at judging the quality of a prompt? If givenhe tool function how will you do?"
        }
    ])

print(response.choices[0].message.content)