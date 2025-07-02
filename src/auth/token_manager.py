from urllib.error import HTTPError
import requests
import json
import os
from dotenv import load_dotenv

script_path = os.path.abspath(__file__)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))

dotenv_path = os.path.join(project_root, '.env')

load_dotenv(dotenv_path=dotenv_path)

CLIENT_ID = os.getenv('BC_CLIENT_ID')
CLIENT_SECRET = os.getenv('BC_CLIENT_SECRET')
TENANT_ID = os.getenv('BC_TENANT_ID')

if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
    raise ValueError("Error: ensure that enviroment variables are set")


URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

def get_token():
    body = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'scope': 'https://api.businesscentral.dynamics.com/.default',
        'client_secret': CLIENT_SECRET,
        'tenant':''
    }

    try:
        response = requests.post(URL, data=body)
        response.raise_for_status()
        token = response.json()['access_token']
        print(f"Access token obtained")
        filename = 'token/token.json'
        message = json.dumps(response.json())
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(message)
        print(f"Access token saved in {filename}")

    except HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
        print(f"Server response: {response.text}")
    except Exception as err:
        print(f"Another error: {err}")