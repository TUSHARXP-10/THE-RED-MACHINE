import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.icicidirect.com/breezeapi/api/v1/customerdetails"

session_token = os.getenv("BREEZE_SESSION_TOKEN").strip('"') if os.getenv("BREEZE_SESSION_TOKEN") else ""
api_key = os.getenv("BREEZE_API_KEY")

payload = json.dumps({
  "SessionToken": session_token,
  "AppKey": api_key
})
headers = {
  'Content-Type': 'application/json',
}

print(f"Using SessionToken: {session_token}")
print(f"Using AppKey: {api_key}")

response = requests.request("GET", url, headers=headers, data=payload)
data = json.loads(response.text)
print(data)