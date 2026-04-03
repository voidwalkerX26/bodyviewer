import requests
import json

api_key = ""  # Replace with your actual API key

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",    
  },
  data=json.dumps({
    "model": "google/gemma-3-4b-it:free",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What is in this image?"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://live.staticflickr.com/3851/14825276609_098cac593d_b.jpg"
            }
          }
        ]
      }
    ]
  })
)

print(response.json())