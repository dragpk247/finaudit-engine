import json
import logging
import httpx
from typing import Dict, Any, Optional
from finaudit.config import settings

logger = logging.getLogger(__name__)

class AIRouter:
    def __init__(self):
        self.desktop_url = settings.desktop_ollama_url
        self.local_url = settings.local_ollama_url
        self.openrouter_key = settings.openrouter_api_key

    async def check_health(self) -> Dict[str, Any]:
        """Checks availability across all 3 tiers."""
        async with httpx.AsyncClient(timeout=1.5) as client:
            desktop_ok = False
            try:
                r = await client.get(f"{self.desktop_url}/api/tags")
                desktop_ok = r.status_code == 200
            except Exception:
                desktop_ok = False

            local_ok = False
            try:
                r = await client.get(f"{self.local_url}/api/tags")
                local_ok = r.status_code == 200
            except Exception:
                local_ok = False

            cloud_ok = bool(self.openrouter_key)

        active_tier = "Tier 3: OpenRouter Cloud"
        if desktop_ok:
            active_tier = f"Tier 1: Desktop GPU ({settings.desktop_model})"
        elif local_ok:
            active_tier = f"Tier 2: Laptop Local ({settings.local_model})"

        return {
            "desktop_gpu": {"online": desktop_ok, "url": self.desktop_url, "model": settings.desktop_model},
            "laptop_local": {"online": local_ok, "url": self.local_url, "model": settings.local_model},
            "openrouter_cloud": {"configured": cloud_ok, "model": settings.openrouter_model},
            "active_tier": active_tier
        }

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Executes prompt using 3-tier fallback hierarchy."""
        async with httpx.AsyncClient(timeout=90.0) as client:
            # 1. Try Desktop GPU
            try:
                payload = {
                    "model": settings.desktop_model,
                    "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                    "stream": False
                }
                res = await client.post(f"{self.desktop_url}/api/generate", json=payload, timeout=45.0)
                if res.status_code == 200:
                    data = res.json()
                    response = data.get("response", "")
                    # Strip <think> tags if present in DeepSeek R1 output
                    if "</think>" in response:
                        response = response.split("</think>")[-1].strip()
                    return response
            except Exception as e:
                logger.warning(f"Tier 1 (Desktop GPU) failed: {e}. Falling back to Tier 2...")

            # 2. Try Laptop Local
            try:
                payload = {
                    "model": settings.local_model,
                    "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                    "stream": False
                }
                res = await client.post(f"{self.local_url}/api/generate", json=payload, timeout=20.0)
                if res.status_code == 200:
                    return res.json().get("response", "")
            except Exception as e:
                logger.warning(f"Tier 2 (Laptop Local) failed: {e}. Falling back to Tier 3...")

            # 3. Fallback to OpenRouter Cloud
            if self.openrouter_key:
                try:
                    headers = {
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://finaudit.local",
                        "X-Title": "FinAudit Engine"
                    }
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})

                    payload = {
                        "model": settings.openrouter_model,
                        "messages": messages,
                        "temperature": 0.2
                    }
                    res = await client.post(settings.openrouter_url, json=payload, headers=headers, timeout=30.0)
                    if res.status_code == 200:
                        data = res.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        raise RuntimeError(f"OpenRouter returned status {res.status_code}: {res.text}")
                except Exception as e:
                    logger.error(f"Tier 3 (OpenRouter) failed: {e}")
                    raise RuntimeError(f"All 3 AI tiers failed to respond: {e}")

            raise RuntimeError("No AI tier available to service request.")

ai_router = AIRouter()
