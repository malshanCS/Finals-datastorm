import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the API key is taken from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI()

async def classify_with_gpt3(prompt: str):
    try:
        # Asynchronously call the OpenAI API if the SDK supports it. For now, it's a regular call.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.5
        )
        # Ensure response is successful and has content
        if response:
            return response.choices[0].message.content
        else:
            return "No valid response received."
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "Error processing your request."