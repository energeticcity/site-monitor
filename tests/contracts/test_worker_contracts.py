"""Contract tests for Cloudflare Worker."""

import os
from typing import Any, Dict

import httpx
import pytest
from pydantic import BaseModel, Field, ValidationError


class WorkerResponse(BaseModel):
    """Worker response schema."""

    source: str
    links: list[str] | None = None
    feeds: list[str] | None = None
    count: int
    diagnostics: Dict[str, Any] | None = None


@pytest.fixture
def worker_base_url() -> str:
    """Get Worker base URL from environment."""
    url = os.getenv("WORKER_BASE_URL", "https://your-worker.workers.dev")
    return url


@pytest.fixture
def skip_if_no_worker() -> None:
    """Skip tests if SKIP_CONTRACT_TESTS is set."""
    if os.getenv("SKIP_CONTRACT_TESTS", "false").lower() == "true":
        pytest.skip("Contract tests skipped (SKIP_CONTRACT_TESTS=true)")


@pytest.mark.contract
def test_discover_endpoint_contract(worker_base_url: str, skip_if_no_worker: None) -> None:
    """Test /discover endpoint returns valid response."""
    client = httpx.Client(timeout=30.0)

    try:
        response = client.post(
            f"{worker_base_url}/discover",
            json={"url": "https://example.com"},
        )

        # Should return 200
        assert response.status_code == 200

        # Should match schema
        data = response.json()
        worker_response = WorkerResponse(**data)

        # Validate required fields
        assert isinstance(worker_response.source, str)
        assert isinstance(worker_response.count, int)
        assert worker_response.count >= 0

        # At least one of links or feeds should exist
        assert worker_response.links is not None or worker_response.feeds is not None

    except httpx.TimeoutException:
        pytest.skip("Worker timeout - may not be available")
    except httpx.ConnectError:
        pytest.skip("Worker not reachable - using fixtures in CI")
    finally:
        client.close()


@pytest.mark.contract
def test_rcmp_fsj_profile_contract(worker_base_url: str, skip_if_no_worker: None) -> None:
    """Test /profiles/rcmp-fsj endpoint returns valid response."""
    client = httpx.Client(timeout=30.0)

    try:
        response = client.post(
            f"{worker_base_url}/profiles/rcmp-fsj",
            json={},
        )

        # Should return 200
        assert response.status_code == 200

        # Should match schema
        data = response.json()
        worker_response = WorkerResponse(**data)

        # Validate required fields
        assert isinstance(worker_response.source, str)
        assert isinstance(worker_response.count, int)
        assert worker_response.count >= 0

    except httpx.TimeoutException:
        pytest.skip("Worker timeout - may not be available")
    except httpx.ConnectError:
        pytest.skip("Worker not reachable - using fixtures in CI")
    finally:
        client.close()


@pytest.mark.contract
def test_response_schema_validation() -> None:
    """Test response schema validation with valid data."""
    valid_data = {
        "source": "html",
        "links": ["https://example.com/post1", "https://example.com/post2"],
        "count": 2,
    }

    response = WorkerResponse(**valid_data)
    assert response.source == "html"
    assert len(response.links) == 2
    assert response.count == 2


@pytest.mark.contract
def test_response_schema_validation_invalid() -> None:
    """Test response schema validation with invalid data."""
    invalid_data = {
        "source": "html",
        # Missing count
    }

    with pytest.raises(ValidationError):
        WorkerResponse(**invalid_data)

