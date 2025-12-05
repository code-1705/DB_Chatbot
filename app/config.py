# In production, you don't just use os.getenv. If an API key is missing, the app should crash 
# immediately with a clear error, not fail silently later. We use pydantic-settings for this.
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Gemini Mongo Chatbot"
    DEBUG_MODE: bool = False
    
    # Secrets (These MUST exist in .env)
    MONGODB_URL: str
    DB_NAME: str = "analytics_db"
    GEMINI_API_KEY: str
    
    # Constants
    SALES_COLLECTION: str = "sales_data"
    HISTORY_COLLECTION: str = "user_chat_history"
    MODEL_NAME: str = "gemini-2.0-flash"

    class Config:
        env_file = ".env"

# Initialize single instance
settings = Settings()