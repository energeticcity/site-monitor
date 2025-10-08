"""Cloudflare Worker client for site discovery."""

from typing import Any, Optional

import httpx
from pydantic import BaseModel, Field

from app.config import settings


class WorkerResponse(BaseModel):
    """Worker response model."""

    source: str
    links: Optional[list[str]] = None
    feeds: Optional[list[str]] = None
    count: int
    diagnostics: Optional[dict[str, Any]] = None


class WorkerClientError(Exception):
    """Worker client error."""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class WorkerClient:
    """Cloudflare Worker client."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def discover(self, url: str) -> WorkerResponse:
        """Discover new posts on a website."""
        response = self._post("/discover", params={"url": url})
        return WorkerResponse(**response)

    def rcmp_fsj(self, months_back: Optional[int] = None) -> WorkerResponse:
        """Get RCMP FSJ posts."""
        params = {"monthsBack": months_back} if months_back is not None else {}
        response = self._post("/profiles/rcmp-fsj", params=params)
        return WorkerResponse(**response)

    def _post(
        self, 
        path: str, 
        body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a POST request to the Worker."""
        url = f"{self.base_url}{path}"

        try:
            response = self.client.post(url, json=body, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise WorkerClientError(
                f"Worker request failed: {e.response.status_code}",
                status_code=e.response.status_code,
                response=e.response.text,
            )
        except httpx.TimeoutException:
            raise WorkerClientError("Worker request timed out")
        except Exception as e:
            raise WorkerClientError(f"Worker request failed: {str(e)}")

    def close(self) -> None:
        """Close the client."""
        self.client.close()

    def __enter__(self) -> "WorkerClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


def get_worker_client() -> WorkerClient:
    """Get a Worker client instance."""
    return WorkerClient(settings.worker_base_url)

