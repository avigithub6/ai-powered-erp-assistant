
import json

import httpx

from app.ai.prompts.answer_generation import ANSWER_GENERATION_PROMPT
from app.ai.prompts.entity_extraction import (
    DATE_METRIC_EXTRACTION_PROMPT,
    ENTITY_EXTRACTION_PROMPT,
    FILTER_EXTRACTION_PROMPT,
)
from app.ai.prompts.intent_classification import INTENT_CLASSIFICATION_PROMPT
from app.ai.tools.schemas import (
    IntentClassification,
    IntentDateRange,
    IntentEntities,
    IntentFilters,
    StructuredIntent,
)
from app.config import settings


class OllamaClient:
    async def _request_structured(
        self,
        system_prompt: str,
        user_content: str,
        response_schema: dict,
        max_tokens: int = 250,
    ) -> dict:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "stream": False,
            "format": response_schema,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "options": {
                "temperature": 0,
                "top_p": 0.1,
                "seed": 42,
                "num_predict": max_tokens,
            },
        }

        timeout = httpx.Timeout(timeout=45.0, connect=5.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

        if not isinstance(result, dict):
            raise TypeError("Invalid Ollama response")

        message = result.get("message")
        if not isinstance(message, dict):
            raise TypeError("Invalid Ollama message")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Ollama returned an empty response")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Ollama returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise TypeError("Ollama response must be a JSON object")

        return parsed

    async def understand_intent(self, question: str) -> StructuredIntent:
        # Step 1: Classify the user's request.
        classification_data = await self._request_structured(
            system_prompt=INTENT_CLASSIFICATION_PROMPT,
            user_content=question,
            response_schema=IntentClassification.model_json_schema(),
            max_tokens=200,
        )

        classification = IntentClassification.model_validate(
            classification_data
        )

        # Out-of-scope requests must never execute ERP tools.
        if classification.request_type == "out_of_scope":
            return StructuredIntent(
                request_type="out_of_scope",
                tool=None,
                intent=classification.intent,
                unsupported_filters=classification.unsupported_filters,
            )

        # Return clarification without running extraction calls.
        if classification.needs_clarification:
            return StructuredIntent(
                request_type="erp",
                tool=classification.tool,
                intent=classification.intent,
                unsupported_filters=classification.unsupported_filters,
                needs_clarification=True,
                clarification_question=(
                    classification.clarification_question
                ),
            )

        extraction_context = question

        # Step 2: Extract entities.
        entity_data = await self._request_structured(
            system_prompt=ENTITY_EXTRACTION_PROMPT,
            user_content=extraction_context,
            response_schema=IntentEntities.model_json_schema(),
            max_tokens=120,
        )

        entities = IntentEntities.model_validate(entity_data)

        # Step 3: Extract filters.
        filter_data = await self._request_structured(
            system_prompt=FILTER_EXTRACTION_PROMPT,
            user_content=extraction_context,
            response_schema=IntentFilters.model_json_schema(),
            max_tokens=120,
        )

        filters = IntentFilters.model_validate(filter_data)

        # Preserve status filters only for tools that support
        # status-based filtering.
        if classification.tool not in {"inventory", "vendor_search"}:
            filters.status = None

        # Do not accept a status invented by the extractor.
        extracted_status = filters.status

        if extracted_status:
            question_lower = question.casefold()
            status_lower = extracted_status.casefold()

            if status_lower not in question_lower:
                filters.status = None

        # Step 4: Extract dates and metric.
        date_metric_schema = {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": ["string", "null"],
                    "format": "date",
                },
                "end_date": {
                    "type": ["string", "null"],
                    "format": "date",
                },
                "metric": {
                    "type": ["string", "null"],
                    "enum": ["revenue", "quantity", "count", None],
                },
            },
            "required": [
                "start_date",
                "end_date",
                "metric",
            ],
        }

        date_metric_data = await self._request_structured(
            system_prompt=DATE_METRIC_EXTRACTION_PROMPT,
            user_content=extraction_context,
            response_schema=date_metric_schema,
            max_tokens=120,
        )

        date_range = IntentDateRange.model_validate(
            {
                "start_date": date_metric_data.get("start_date"),
                "end_date": date_metric_data.get("end_date"),
            }
        )

        metric = date_metric_data.get("metric")

        if metric not in {None, "revenue", "quantity", "count"}:
            raise ValueError("Invalid extracted metric")

        # Count must be explicitly requested.
        if metric == "count":
            count_requested = await self._request_structured(
                system_prompt=(
                    "Determine whether the original user question "
                    "explicitly asks for the number or count of records. "
                    "A request to list, show or find records is not a "
                    "count request. Return JSON with requested=true "
                    "only for explicit count questions."
                ),
                user_content=question,
                response_schema={
                    "type": "object",
                    "properties": {
                        "requested": {"type": "boolean"},
                    },
                    "required": ["requested"],
                },
                max_tokens=30,
            )

            if count_requested.get("requested") is not True:
                metric = None

        # Step 5: Combine all validated results.
        return StructuredIntent(
            request_type="erp",
            tool=classification.tool,
            intent=classification.intent,
            entities=entities,
            filters=filters,
            date_range=date_range,
            metric=metric,
            unsupported_filters=classification.unsupported_filters,
        )

    async def generate_answer(
        self,
        question: str,
        tool: str,
        data: dict | list,
    ) -> str:
        payload = {
            "model": settings.OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": ANSWER_GENERATION_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"User question:\n{question}\n\n"
                        f"Selected ERP operation:\n{tool}\n\n"
                        f"Authorized backend data:\n"
                        f"{json.dumps(data, ensure_ascii=False)}"
                    ),
                },
            ],
            "options": {
                "temperature": 0.2,
                "top_p": 0.8,
                "seed": 42,
                "num_predict": 250,
            },
        }

        timeout = httpx.Timeout(timeout=45.0, connect=5.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

        if not isinstance(result, dict):
            raise TypeError("Invalid Ollama answer response")

        message = result.get("message")
        if not isinstance(message, dict):
            raise TypeError("Invalid Ollama answer message")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Ollama returned an empty answer")

        return content.strip()
