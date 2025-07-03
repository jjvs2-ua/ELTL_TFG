import sys
import os
import json
from dotenv import load_dotenv


project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from auth.token_manager import get_new_token
from data_ingestor.api_cliente import ApiClient
from messaging.publisher import publish_message


def main():

    load_dotenv(os.path.join(project_root, '.env'))

    BASE_URL = os.getenv('BC_BASE_URL')
    EXCHANGE_NAME = os.getenv('EXCHANGE_NAME')
    if not all([BASE_URL, EXCHANGE_NAME]):
        raise ValueError("[ERROR] Make sure BC_BASE_URL and EXCHANGE_NAME are set in the .env file")

    try:
        with open(os.path.join(project_root, 'PBI_endpoints.json'), 'r') as f:
            ALL_ENDPOINTS = json.load(f)
    except FileNotFoundError:
        print("[ERROR] PBI_endpoints.json file not found.")
        sys.exit(1)

    # --- 2. Argument Handling (using sys.argv) ---
    endpoints_to_process = []
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1].lower() == 'all'):
        endpoints_to_process = ALL_ENDPOINTS
    elif len(sys.argv) == 2 and sys.argv[1] in ALL_ENDPOINTS:
        endpoints_to_process = [sys.argv[1]]
    else:
        print(f"[ERROR] Invalid argument: '{sys.argv[1] if len(sys.argv) > 1 else ''}'. Use 'all' or a valid endpoint.")
        sys.exit(1)

    # --- 3. Pipeline Execution ---
    print("[INFO] Starting ingestion pipeline...")
    token = get_new_token()
    if not token:
        print("[CRITICAL] Could not get token. Aborting.")
        sys.exit(1)

    api_client = ApiClient(base_url=BASE_URL, token=token)

    for endpoint in endpoints_to_process:
        print(f"--- Processing endpoint: {endpoint} ---")

        data = api_client.get_all_data(endpoint)

        if data:
            routing_key = f"{endpoint}.info"
            success = publish_message(EXCHANGE_NAME, routing_key, data)
            if not success:
                print(f"[ERROR] Could not publish message for {endpoint}")
        else:
            print(f"[WARN] No data received for {endpoint}. Skipping publication.")

    print("\n[INFO] Ingestion pipeline finished.")


if __name__ == '__main__':
    main()