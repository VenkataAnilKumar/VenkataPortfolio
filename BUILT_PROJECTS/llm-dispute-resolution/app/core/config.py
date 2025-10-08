import os
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    db_url: str = os.getenv("DB_URL", "sqlite+aiosqlite:///./disputes.db")
    mock_llm: bool = os.getenv("MOCK_LLM", "1") == "1"
    api_key: str | None = os.getenv("API_KEY")
    token_budget_per_case: int = int(os.getenv("TOKEN_BUDGET_PER_CASE", "6000"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
