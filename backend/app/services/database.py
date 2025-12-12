# This file handles the connection and the raw execution. It knows nothing about Gemini.
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Dict
from app.config import settings
from app.utils import deserialize_pipeline_dates # We'll move the helper here

class DatabaseService:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DB_NAME]

    async def get_history(self, user_id: str, limit: int = 50):
        doc = await self.db[settings.HISTORY_COLLECTION].find_one({"user_id": user_id})
        if not doc:
            return []
        return doc.get("history", [])[-limit:]

    async def save_interaction(self, user_id: str, question: str, answer: str):
        entry = {"question": question, "answer": answer, "timestamp": datetime.utcnow()}
        await self.db[settings.HISTORY_COLLECTION].update_one(
            {"user_id": user_id}, 
            {"$push": {"history": entry}}, 
            upsert=True
        )

    async def execute_pipeline(self, pipeline: List[Dict]):
        if not pipeline:
            return []
        
        # Helper imported from utils.py
        pipeline = deserialize_pipeline_dates(pipeline)
        
        try:
            cursor = self.db[settings.SALES_COLLECTION].aggregate(pipeline)
            results = await cursor.to_list(length=100)
            
            # Simple serialization
            serialized = []
            for doc in results:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"]) # Handle ObjectId
                if "date" in doc and isinstance(doc["date"], datetime):
                    doc["date"] = doc["date"].isoformat()
                serialized.append(doc)
            return serialized
        except Exception as e:
            print(f"DB Error: {e}") # Replace with logger in step 5
            return []

db_service = DatabaseService()