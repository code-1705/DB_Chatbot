import json
from fastapi import FastAPI
from app.config import settings
from app.models import ChatInput
# Import the instances we created in the services files
from app.services.database import db_service 
from app.services.llm import generate_query_intent, synthesize_response, general_chat_response

app = FastAPI(title=settings.APP_NAME)

from fastapi.middleware.cors import CORSMiddleware

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HERE IS YOUR API ENDPOINT ---
@app.post("/chat/{user_id}")
async def chat_endpoint(user_id: str, input_data: ChatInput):
    # 1. Get History
    # We use the db_service method now
    history = await db_service.get_history(user_id, limit=50)

    # 2. Intent
    # We use the function imported from services.llm
    intent = await generate_query_intent(input_data.message, history, input_data.company)

    response_text = ""

    # 3. Execution Logic
    if intent.is_database_query:
        # Path A: Data
        # We use db_service to execute the pipeline
        results = await db_service.execute_pipeline(intent.pipeline)
        
        db_context = json.dumps(results, indent=2) if results else "[] (No matches)"
        response_text = await synthesize_response(input_data.message, db_context)
    else:
        # Path B: General Chat
        response_text = await general_chat_response(input_data.message, history)

    # 4. Save Interaction
    # --- HERE IS WHERE THE SAVE HAPPENS ---
    await db_service.save_interaction(user_id, input_data.message, response_text)

    return {
        "response": response_text,
        "debug_pipeline": intent.pipeline if intent.is_database_query else None
    }

@app.get("/history/{user_id}")
async def get_history_endpoint(user_id: str, limit: int = 20):
    # We reuse the service logic here too
    history = await db_service.get_history(user_id, limit=limit)
    return {"history": history}