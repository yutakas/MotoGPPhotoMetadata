import openai
import base64
import json
import cv2

from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


def get_openai_analysis(cv2_image):
    # Convert the OpenCV image to base64
    _, buffer = cv2.imencode(".jpg", cv2_image)
    image_data = base64.b64encode(buffer).decode("utf-8")

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                        },
                        {
                            "type": "text",
                            "text": "This is an image of a MotoGP motorcycle. Please analyze the team name, sponsor logos, and bike color. Return only 'motogp_team', 'sponsor_names', 'bike_color' and 'logos' in JSON format. The bike color must be the one primary color ",
                        }
                    ],
                }
            ],
        )
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None

    content = response.choices[0].message.content
    content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Failed to parse OpenAI response as JSON: {e}\nContent: {content}")
        return None