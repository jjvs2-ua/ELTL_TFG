from urllib.error import HTTPError
import requests
import logging
from config import log_config

log_config.setup_logging("logs/main_ingestion")
logger = logging.getLogger(__name__)


class ApiClient:


    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token


    def get_all_data(self, endpoint):
        try:
            URL = self.base_url + endpoint
            token = self.token
            #print(f'\n Endpoint: \n {endpoint} \n')
            logger.info(f' Endpoint:  {endpoint} ')
            Auth_token = f'Bearer {token}'
            headers = {
                'Authorization': Auth_token,
                'Content-Type': 'application/json'
            }
            response = requests.get(URL, headers=headers)
            response.raise_for_status()
            data = response.json()['value']
            logger.info(f' Successfully fetched data {endpoint} ')
            return data

        except HTTPError as http_err:
            #print(f"Error HTTP ocurrido: {http_err}")
            logger.error(f'HTTP error occurred: {http_err}')
            #print(f"Respuesta del servidor: {response.text}")
            return None
        except Exception as err:
            #print(f"Otro error ocurrido: {err}")
            logger.error(f'Other error occurred: {err}')
            return None



