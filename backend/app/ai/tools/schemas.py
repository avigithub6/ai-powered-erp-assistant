from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolArguments(BaseModel):
    limit: int = Field(default=5, ge=1, le=10)

    model_config = ConfigDict(extra="forbid")


class ToolSelection(BaseModel):
    tool: Literal[
        "dashboard_summary",
        "sales_trend",
        "top_products",
        "top_vendors",
        "inventory",
        "low_stock",
        "sales_purchase_comparison",
        "vendor_search",
    ]

    arguments: ToolArguments = Field(default_factory=ToolArguments)

    model_config = ConfigDict(extra="forbid")
