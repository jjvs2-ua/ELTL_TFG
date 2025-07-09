from datetime import datetime
import json
import os
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
    
    def _set_last_load(self, last_date):
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'last_load.json')
            config_path = os.path.abspath(config_path)
            data = {"last_load_date": last_date}
            with open(config_path, 'w') as file:
                json.dump(data, file, indent=4)

        except Exception as err:
            logger.error(f'Other error occurred: {err}')
 

    def _get_last_load(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'last_load.json')
            config_path = os.path.abspath(config_path)
            with open(config_path, 'r') as file:
                data = json.load(file)
                return data.get("last_load_date", "")  # Devuelve None si no existe la clave
        except Exception as err:
            logger.error(f'Other error occurred: {err}')
            return ""
         


    def get_all_data(self, endpoint):
        try:
            last_load = self._get_last_load()
            URL = self.base_url + endpoint + f"?$filter=systemModifiedAt ge {last_load}Z"
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
            load_date_hour = datetime.now().isoformat()
            self._set_last_load(load_date_hour)
            logger.info(f' Successfully fetched data {endpoint} : ')
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



