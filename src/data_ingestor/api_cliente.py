from urllib.error import HTTPError
import requests
import json

class ApiClient:


    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token


    def get_all_data(self, endpoint):
        try:
            URL = self.base_url + endpoint
            token = self.token
            print(f'\n Endpoint: \n {endpoint} \n')
            Auth_token = f'Bearer {token}'
            headers = {
                'Authorization': Auth_token,
                'Content-Type': 'application/json'
            }
            response = requests.get(URL, headers=headers)
            response.raise_for_status()
            data = response.json()['value']
            return data

        except HTTPError as http_err:
            print(f"Error HTTP ocurrido: {http_err}")
            print(f"Respuesta del servidor: {response.text}")
            return None
        except Exception as err:
            print(f"Otro error ocurrido: {err}")
            return None



