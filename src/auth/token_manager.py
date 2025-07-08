import requests
import json
import os
from dotenv import load_dotenv
import logging
from config import log_config

# Configuración del logging
log_config.setup_logging("logs/main_ingestion")
logger = logging.getLogger(__name__)

# Rutas y carga de variables de entorno
script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_path)))
dotenv_path = os.path.join(project_root, 'config/.env')
load_dotenv(dotenv_path=dotenv_path)

CLIENT_ID = os.getenv('BC_CLIENT_ID')
CLIENT_SECRET = os.getenv('BC_CLIENT_SECRET')
TENANT_ID = os.getenv('BC_TENANT_ID')


def get_new_token():
    """
    Obtiene un nuevo token de autenticación de Microsoft Entra ID.
    """
    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        # Las excepciones son correctas como están, no se loguean de la misma manera
        raise ValueError(".env file is incomplete")

    URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    body = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'scope': 'https://api.businesscentral.dynamics.com/.default',
        'client_secret': CLIENT_SECRET
    }

    try:
        response = requests.post(URL, data=body)
        response.raise_for_status()  # Lanza una excepción para errores HTTP (4xx o 5xx)

        token_data = response.json()
        access_token = token_data.get('access_token')

        # Guarda la respuesta completa en el fichero
        os.makedirs('token', exist_ok=True)
        with open('token/token.json', 'w', encoding='utf-8') as file:
            json.dump(token_data, file, indent=4)

        # print("[INFO] Token guardado en token/token.json")
        logger.info("Token saved : token/token.json")

        return access_token

    except Exception as e:
        # print(f"[ERROR] No se pudo obtener un nuevo token: {e}")
        logger.error(f"Could not get new token: {e}", exc_info=True)
        return None