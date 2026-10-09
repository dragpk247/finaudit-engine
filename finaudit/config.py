import os
from pydantic import BaseModel

class Settings(BaseModel):
    # Desktop GPU Ollama (Primary)
    desktop_ollama_url: str = os.getenv("DESKTOP_OLLAMA_URL", "http://100.86.159.86:11434")
    desktop_model: str = os.getenv("DESKTOP_MODEL", "deepseek-r1:14b")
    desktop_coder_model: str = os.getenv("DESKTOP_CODER_MODEL", "qwen2.5-coder:14b")

    # Local Laptop Ollama (Secondary fallback)
    local_ollama_url: str = os.getenv("LOCAL_OLLAMA_URL", "http://127.0.0.1:11434")
    local_model: str = os.getenv("LOCAL_MODEL", "qwen2.5-coder:1.5b")

    # OpenRouter (Cloud fallback)
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

settings = Settings()
