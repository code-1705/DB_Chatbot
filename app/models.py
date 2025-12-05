# Keep your data definitions clean.
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatInput(BaseModel):
    message: str
    company: str 

class PipelineResponse(BaseModel):
    reasoning: str = Field(description="Logic used to derive the query")
    is_database_query: bool
    pipeline: List[Dict[str, Any]] = []