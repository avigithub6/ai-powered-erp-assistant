from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AIQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class AIQueryResponse(BaseModel):
    answer: str
    tool_used: str | None = None
    source: str
    data: Any = None