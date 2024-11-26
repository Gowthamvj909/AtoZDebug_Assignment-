from pymongo import MongoClient
from core.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["library_management"]
users_collection = db["users"]
books_collection = db["books"]