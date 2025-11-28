from httpx import AsyncClient
import pytest

from models import Customer


@pytest.mark.asyncio
async def test_get_all_customers(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Bütün müştəriləri gətir"""
    response = await admin_client.get("/api/admin/customers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(sample_customers)
