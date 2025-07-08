import logging
import sys

def setup_logging(filename):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
        handlers=[
            logging.FileHandler(f"{filename}.log"),
            logging.StreamHandler(sys.stdout) # Usar sys.stdout para asegurar la salida
        ]
    )
    logging.getLogger('pika').setLevel(logging.WARNING)