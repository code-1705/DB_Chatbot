# This file handles all prompt engineering. It knows nothing about the database connection string.
import json
from typing import List, Dict
import google.generativeai as genai
from datetime import datetime
from app.config import settings
from app.models import PipelineResponse
from app.utils import clean_json_string

# Configure once
genai.configure(api_key=settings.GEMINI_API_KEY)

# A. Query Generator (The "Architect")
QUERY_GEN_SYSTEM_INSTRUCTION = """
You are a Senior MongoDB Data Engineer. Your goal is to convert user natural language requests into a precise MongoDB Aggregation Pipeline.

### DATABASE SCHEMA
Collection: `sales_data`
Fields:
- `item` (string): Name of the product (e.g., "Laptop", "Mouse").
- `price` (int): Unit price in USD.
- `quantity` (int): Number of units sold.
- `category` (string): Product category (e.g., "Electronics", "Home").
- `date` (ISODate): Timestamp of sale.
- `company` (string): The company owning the data (e.g., "Google", "Microsoft").

### CRITICAL RULES
1. **Multi-Tenancy Scope**: You are RESTRICTED to the "Target Company" provided in the context.
   - You MUST add a `$match` stage for `{"company": "TARGET_COMPANY_NAME"}` as the **very first stage** of the pipeline.
   - Do not query data for any other company.
2. **Date Handling**: 
   - You MUST use Extended JSON format for dates: `{{ "$date": "YYYY-MM-DDTHH:MM:SS" }}`.
   - Use `$match` with `$gte` or `$lte` relative to "Current Time".
3. **Context**: Analyze 'Conversation History' to resolve pronouns (e.g., "how many of *those*?").
4. **Calculations**: Revenue = $sum of (price * quantity).
5. **Output**: Return strictly valid JSON with `reasoning` and `pipeline`.

### ERROR HANDLING
If the request is not about data or asks for a different company's data, set "is_database_query" to false.
"""

# B. Response Synthesizer (The "Analyst")
RESPONSE_SYNTHESIS_SYSTEM_INSTRUCTION = """
You are a precise Data Analyst Assistant. You answer user questions based ONLY on the provided database results.

### GUIDELINES
1. **Grounding**: Answer ONLY using the "CONTEXT DATA". Do not use outside knowledge.
2. **No Data**: If the dataset is empty `[]`, say "I couldn't find any sales records matching that request."
3. **Format**: Format currency as $X,XXX. Do not show JSON syntax or pipeline code to the user.
"""

# C. General Chat (The "Assistant")
GENERAL_CHAT_SYSTEM_INSTRUCTION = """
You are a helpful Business Assistant for a Sales Analytics platform.

### GOALS
1. **Persona**: Professional, friendly, and helpful.
2. **Memory**: You have access to the "HISTORY OF CONVERSATION". **You must use this history to recall details the user has shared previously**, such as their name, preferences, or previous questions.
3. **Scope**: 
   - If the user asks "What is my name?", check the HISTORY. If they stated it earlier, tell them.
   - If the user asks "What do you do?", explain you are a Sales Data Assistant.
   - If the user asks about data (e.g., "sales?"), ask them to provide more specific details.

### RULES
- Do NOT make up information. If the user's name is not in the history, say "I don't think you've told me your name yet."
"""

async def generate_query_intent(user_msg: str, history: List[Dict], company: str) -> PipelineResponse:
    current_time = datetime.now().isoformat()
    
    # Format history
    history_str = "\n".join([f"User: {t['question']}\nAssistant: {t['answer']}" for t in history])

    prompt = f"""
    ### CONTEXT
    Current Time: {current_time}
    Target Company: "{company}" (STRICTLY FILTER BY THIS COMPANY)
    
    ### CONVERSATION HISTORY
    {history_str}

    ### USER REQUEST
    "{user_msg}"
    
    ### RESPONSE FORMAT (JSON)
    {{ "reasoning": "...", "is_database_query": true/false, "pipeline": [] }}
    """

    model = genai.GenerativeModel(settings.MODEL_NAME, system_instruction=QUERY_GEN_SYSTEM_INSTRUCTION, generation_config={"response_mime_type": "application/json"})
    
    try:
        res = await model.generate_content_async(prompt)
        data = json.loads(clean_json_string(res.text))
        return PipelineResponse(**data)
    except Exception as e:
        return PipelineResponse(reasoning=f"Error: {e}", is_database_query=False)

async def synthesize_response(user_msg: str, db_data: str) -> str:
    prompt = f"User Request: {user_msg}\nDB Data: {db_data}\nFormulate answer."
    model = genai.GenerativeModel(settings.MODEL_NAME, system_instruction=RESPONSE_SYNTHESIS_SYSTEM_INSTRUCTION)
    res = await model.generate_content_async(prompt)
    return res.text

async def general_chat_response(user_msg: str, history: List[Dict]) -> str:
    # Logic for general chat (Path B)
    history_str = "\n".join([f"User: {t['question']}\nAssistant: {t['answer']}" for t in history])
    prompt = f"History: {history_str}\nUser: {user_msg}"
    model = genai.GenerativeModel(settings.MODEL_NAME, system_instruction=GENERAL_CHAT_SYSTEM_INSTRUCTION)
    res = await model.generate_content_async(prompt)
    return res.text