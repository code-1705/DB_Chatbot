import re
from datetime import datetime
from typing import Any

def clean_json_string(json_str: str) -> str:
    """Removes Markdown code blocks provided by LLMs."""
    cleaned = re.sub(r"```json\n?|```", "", json_str).strip()
    return cleaned

def deserialize_pipeline_dates(obj: Any) -> Any:
    """
    Recursively converts {"$date": "ISO_STRING"} from LLM JSON 
    into actual Python datetime objects that Motor/PyMongo can execute.
    """
    if isinstance(obj, dict):
        if len(obj) == 1 and "$date" in obj:
            try:
                # remove 'Z' if present, python fromisoformat handles offsets or naive
                date_str = obj["$date"].replace('Z', '+00:00') 
                return datetime.fromisoformat(date_str)
            except ValueError:
                return obj["$date"]
        return {k: deserialize_pipeline_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deserialize_pipeline_dates(item) for item in obj]
    return obj