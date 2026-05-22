import os
import requests
from dotenv import load_dotenv

# Load your secret token
load_dotenv()
TOKEN = os.getenv("META_ACCESS_TOKEN")

# This URL asks Meta for the list of Facebook pages your token has access to
url = f"https://graph.facebook.com/v25.0/me/accounts?access_token={TOKEN}"

response = requests.get(url)

if response.status_code == 200:
    print("✅ Success! Connection established.")
    print("Here are your connected pages:")
    print(response.json())
else:
    print("❌ Connection failed.")
    print(response.json())
