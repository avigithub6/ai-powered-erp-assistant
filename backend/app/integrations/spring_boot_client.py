
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class SpringBootERPClient:
    """Secure HTTP client for the internal Spring Boot ERP service."""

    def __init__(self) -> None:
        self.base_url = settings.SPRING_BOOT_ERP_BASE_URL.rstrip("/")
        self.internal_token = settings.SPRING_BOOT_INTERNAL_TOKEN

    async def get_sales_orders(
        self,
        tenant_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        if tenant_id <= 0:
            raise ValueError("Invalid tenant identifier")

        if not self.internal_token:
            logger.error("Spring Boot internal token is not configured")
            raise RuntimeError("ERP integration is not configured")

        headers = {
            "X-Internal-Service-Token": self.internal_token,
            "X-Tenant-Id": str(tenant_id),
        }

        params = {
            "limit": limit,
            "offset": offset,
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/internal/erp/sales/orders",
                    headers=headers,
                    params=params,
                )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException as exc:
            logger.error("Spring Boot ERP request timed out")
            raise RuntimeError("ERP service request timed out") from exc

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Spring Boot ERP returned HTTP status %s",
                exc.response.status_code,
            )
            raise RuntimeError("ERP service request failed") from exc

        except httpx.RequestError as exc:
            logger.error("Spring Boot ERP connection failed")
            raise RuntimeError("ERP service is unavailable") from exc
