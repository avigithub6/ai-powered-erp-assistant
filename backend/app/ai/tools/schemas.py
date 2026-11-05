
from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

ApprovedTool = Literal[
    "dashboard_summary",
    "sales_trend",
    "top_products",
    "top_vendors",
    "inventory",
    "low_stock",
    "sales_purchase_comparison",
    "vendor_search",
    "sales_summary",
    "purchase_summary",
]


class ToolArguments(BaseModel):
    limit: int = Field(default=5, ge=1, le=10)

    model_config = ConfigDict(extra="forbid")


class IntentEntities(BaseModel):
    vendor_name: str | None = Field(default=None, max_length=150)
    product_name: str | None = Field(default=None, max_length=150)
    customer_name: str | None = Field(default=None, max_length=150)
    sku: str | None = Field(default=None, max_length=80)

    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "vendor_name",
        "product_name",
        "customer_name",
        "sku",
        mode="before",
    )
    @classmethod
    def normalize_empty_entities(cls, value):
        if isinstance(value, str) and value.strip().lower() in {
            "null",
            "none",
            "",
        }:
            return None

        return value


class IntentFilters(BaseModel):
    category: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    status: str | None = Field(default=None, max_length=30)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def normalize_filters(self):
        empty_values = {
            "all",
            "any",
            "none",
            "null",
            "unknown",
            "not specified",
        }

        operation_names = {
            "sale",
            "sales",
            "purchase order",
            "purchase",
            "dashboard",
            "inventory",
            "vendor",
            "vendor search",
            "sales summary",
            "purchase summary",
            "dashboard summary",
            "sales trend",
            "top products",
            "top vendors",
            "sales purchase comparison",
        }

        for field_name in ("category", "location", "status"):
            value = getattr(self, field_name)

            if value and value.strip().lower() in empty_values:
                setattr(self, field_name, None)

        if (
            self.category
            and self.category.strip().lower() in operation_names
        ):
            self.category = None

        return self


class IntentDateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError("start_date cannot be after end_date")

        return self


class IntentClassification(BaseModel):
    request_type: Literal["erp", "out_of_scope"] = "erp"
    tool: ApprovedTool | None = None
    intent: str | None = Field(default=None, max_length=50)
    unsupported_filters: list[str] = Field(default_factory=list)
    needs_clarification: bool = False
    clarification_question: str | None = Field(
        default=None,
        max_length=500,
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("unsupported_filters")
    @classmethod
    def validate_unsupported_filters(cls, value):
        return list(
            dict.fromkeys(
                item.strip().lower()
                for item in value
                if isinstance(item, str) and item.strip()
            )
        )

    @model_validator(mode="after")
    def validate_classification(self):
        if self.request_type == "out_of_scope":
            if self.tool is not None:
                raise ValueError(
                    "Out-of-scope requests cannot select an ERP tool"
                )

            if self.needs_clarification:
                raise ValueError(
                    "Out-of-scope requests cannot request ERP clarification"
                )

        elif self.tool is None:
            raise ValueError(
                "ERP requests must select an approved tool"
            )

        if self.needs_clarification and not self.clarification_question:
            raise ValueError(
                "clarification_question is required when clarification is needed"
            )

        return self


class IntentExtraction(BaseModel):
    entities: IntentEntities = Field(default_factory=IntentEntities)
    filters: IntentFilters = Field(default_factory=IntentFilters)
    date_range: IntentDateRange = Field(default_factory=IntentDateRange)
    metric: Literal["revenue", "quantity", "count"] | None = None

    model_config = ConfigDict(extra="forbid")


class StructuredIntent(BaseModel):
    request_type: Literal["erp", "out_of_scope"] = "erp"
    tool: ApprovedTool | None = None
    intent: str | None = Field(default=None, max_length=50)
    arguments: ToolArguments = Field(default_factory=ToolArguments)
    entities: IntentEntities = Field(default_factory=IntentEntities)
    filters: IntentFilters = Field(default_factory=IntentFilters)
    date_range: IntentDateRange = Field(default_factory=IntentDateRange)
    metric: Literal["revenue", "quantity", "count"] | None = None
    unsupported_filters: list[str] = Field(default_factory=list)
    needs_clarification: bool = False
    clarification_question: str | None = Field(
        default=None,
        max_length=500,
    )

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_structured_intent(self):
        if self.request_type == "out_of_scope":
            if self.tool is not None:
                raise ValueError(
                    "Out-of-scope requests cannot execute an ERP tool"
                )

        elif self.tool is None:
            raise ValueError(
                "ERP requests must have an approved tool"
            )

        if self.needs_clarification and not self.clarification_question:
            raise ValueError(
                "clarification_question is required when clarification is needed"
            )

        return self
