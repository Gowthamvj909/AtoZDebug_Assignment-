from decouple import config
from pathlib import Path

MONGO_URI = config("MONGO_URI", default="mongodb://localhost:27017")
SECRET_KEY = config("SECRET_KEY", default="mysecret")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Ensure the upload directory exists