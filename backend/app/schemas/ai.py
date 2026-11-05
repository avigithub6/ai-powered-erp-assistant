from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AIIntentEntities(BaseModel):
    vendor_name: str | None = None
    product_name: str | None = None
    customer_name: str | None = None
    sku: str | None = None

    model_config = ConfigDict(extra="forbid")


class AIIntentFilters(BaseModel):
    category: str | None = None
    location: str | None = None
    status: str | None = None

    model_config = ConfigDict(extra="forbid")


class AIIntentDateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    model_config = ConfigDict(extra="forbid")


class AIQueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)

    model_config = ConfigDict(extra="forbid")


class AIQueryResponse(BaseModel):
    answer: str
    tool_used: str | None = None
    source: str
    data: Any = None

    # Optional structured intent information
    intent: str | None = None
    entities: AIIntentEntities | None = None
    filters: AIIntentFilters | None = None
    date_range: AIIntentDateRange | None = None
    needs_clarification: bool | None = None
    clarification_question: str | None = None