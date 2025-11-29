import pytest
from httpx import AsyncClient

from models.customer import Customer


# ==================== GET ALL TESTS ====================


@pytest.mark.asyncio
async def test_get_all_customers(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Bütün müştəriləri gətir"""
    response = await admin_client.get("/api/admin/customers/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(sample_customers)

    # İlk müştərinin strukturunu yoxla
    if data:
        customer = data[0]
        assert "id" in customer
        assert "email" in customer
        assert "name" in customer
        assert "created_at" in customer


@pytest.mark.asyncio
async def test_get_all_customers_empty(admin_client: AsyncClient):
    """Boş müştəri siyahısı"""
    response = await admin_client.get("/api/admin/customers/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


# ==================== GET BY ID TESTS ====================


@pytest.mark.asyncio
async def test_get_customer_by_id(admin_client: AsyncClient, sample_customers: list[Customer]):
    """ID ilə müştəri gətir"""
    customer_id = sample_customers[0].id

    response = await admin_client.get(f"/api/admin/customers/{customer_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == customer_id
    assert "email" in data
    assert "name" in data
    assert "phone" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_customer_not_found(admin_client: AsyncClient):
    """Mövcud olmayan müştəri"""
    response = await admin_client.get("/api/admin/customers/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_customer_invalid_id(admin_client: AsyncClient):
    """Yanlış ID formatı"""
    response = await admin_client.get("/api/admin/customers/invalid")
    assert response.status_code == 422


# ==================== UPDATE TESTS ====================


@pytest.mark.asyncio
async def test_update_customer(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Müştəri məlumatlarını yenilə"""
    customer_id = sample_customers[0].id

    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "phone": "+994501234567"
    }

    response = await admin_client.put(
        f"/api/admin/customers/{customer_id}",
        json=update_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == "Updated Name"
    assert data["email"] == "updated@example.com"
    assert data["phone"] == "+994501234567"


@pytest.mark.asyncio
async def test_update_customer_partial(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Qismən məlumat yenilə"""
    customer_id = sample_customers[0].id
    original_email = sample_customers[0].email

    update_data = {
        "name": "Only Name Changed"
    }

    response = await admin_client.put(
        f"/api/admin/customers/{customer_id}",
        json=update_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Only Name Changed"
    assert data["email"] == original_email  # Email dəyişməyib


@pytest.mark.asyncio
async def test_update_customer_not_found(admin_client: AsyncClient):
    """Mövcud olmayan müştərini yenilə"""
    update_data = {
        "name": "Test Name"
    }

    response = await admin_client.put(
        "/api/admin/customers/99999",
        json=update_data
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_customer_invalid_email(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Yanlış email formatı"""
    customer_id = sample_customers[0].id

    update_data = {
        "email": "invalid-email"
    }

    response = await admin_client.put(
        f"/api/admin/customers/{customer_id}",
        json=update_data
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_customer_empty_data(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Boş məlumatla yeniləmə"""
    customer_id = sample_customers[0].id

    response = await admin_client.put(
        f"/api/admin/customers/{customer_id}",
        json={}
    )
    assert response.status_code == 200  # Heç nə dəyişmir, amma uğurludur


# ==================== DELETE TESTS ====================


@pytest.mark.asyncio
async def test_delete_customer(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Müştərini sil"""
    customer_id = sample_customers[0].id

    response = await admin_client.delete(f"/api/admin/customers/{customer_id}")
    assert response.status_code == 200

    # Yoxla ki, müştəri silinib
    get_response = await admin_client.get(f"/api/admin/customers/{customer_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_customer_not_found(admin_client: AsyncClient):
    """Mövcud olmayan müştərini sil"""
    response = await admin_client.delete("/api/admin/customers/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_customer_invalid_id(admin_client: AsyncClient):
    """Yanlış ID formatı ilə silmə"""
    response = await admin_client.delete("/api/admin/customers/invalid")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_customer_twice(admin_client: AsyncClient, sample_customers: list[Customer]):
    """Eyni müştərini iki dəfə sil"""
    customer_id = sample_customers[0].id

    # İlk silmə
    response1 = await admin_client.delete(f"/api/admin/customers/{customer_id}")
    assert response1.status_code == 200

    # İkinci silmə (artıq mövcud deyil)
    response2 = await admin_client.delete(f"/api/admin/customers/{customer_id}")
    assert response2.status_code == 404


# ==================== AUTHORIZATION TESTS ====================


@pytest.mark.asyncio
async def test_get_customers_without_admin(client: AsyncClient):
    """Admin olmadan müştərilərə giriş (əgər auth varsa)"""
    response = await client.get("/api/admin/customers/")
    assert response.status_code in [401, 403]  # Unauthorized or Forbidden


@pytest.mark.asyncio
async def test_update_customer_without_admin(client: AsyncClient):
    """Admin olmadan yeniləmə"""
    update_data = {"name": "Test"}

    response = await client.put("/api/admin/customers/1", json=update_data)
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_delete_customer_without_admin(client: AsyncClient):
    """Admin olmadan silmə"""
    response = await client.delete("/api/admin/customers/1")
    assert response.status_code in [401, 403]