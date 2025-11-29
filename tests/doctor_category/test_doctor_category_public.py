# tests/doctor_category/test_doctor_category_public.py
"""
Doctor Category Public API Tests

Tests for public endpoints that don't require authentication.
Routes: /doctor_categories/
"""

import pytest
from httpx import AsyncClient

from models.doctor_category import DoctorCategory
from schemas.doctor_category_schema import DoctorCategoryList


# ==========================================
# GET / - Get All Categories (Partial Data)
# ==========================================

@pytest.mark.asyncio
async def test_get_all_categories_empty(client: AsyncClient):
    """Test GET / when no categories exist"""
    response = await client.get("/api/doctor_categories/")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_categories_with_data(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategoryList]
):
    """Test GET / returns all categories with partial data"""
    response = await client.get("/api/doctor_categories/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check count
    assert len(data) == 5
    
    # Check first category structure (partial data only)
    first_category = data[0]
    assert "id" in first_category
    assert "title" in first_category
    assert "slug" in first_category
    assert "image" in first_category
    
    # These fields should NOT be in partial response
    assert "keywords" not in first_category
    assert "created_at" not in first_category
    assert "updated_at" not in first_category


@pytest.mark.asyncio
async def test_get_all_categories_returns_correct_fields(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that partial data contains exactly the expected fields"""
    response = await client.get("/api/doctor_categories/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify specific category data
    cardiology = next((c for c in data if c["slug"] == "kardiologiya"), None)
    assert cardiology is not None
    assert cardiology["title"] == "Kardiologiya"
    assert cardiology["image"] == "cardiology.jpg"
    
    # Check that all categories have exactly 4 fields
    for category in data:
        assert len(category) == 4  # id, title, slug, image


# ==========================================
# GET /{slug} - Get Category by Slug
# ==========================================

@pytest.mark.asyncio
async def test_get_category_by_slug_success(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test GET /{slug} returns complete category data"""
    response = await client.get("/api/doctor_categories/kardiologiya")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check all fields are present (full data)
    assert data["title"] == "Kardiologiya"
    assert data["slug"] == "kardiologiya"
    assert data["keywords"] == "ürək, qan dövranı, kardiovaskulyar"
    assert data["image"] == "cardiology.jpg"
    assert "created_at" in data
    assert "updated_at" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_get_category_by_slug_not_found(client: AsyncClient):
    """Test GET /{slug} with non-existent slug"""
    response = await client.get("/api/doctor_categories/non-existent-slug")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_category_by_slug_case_sensitive(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that slug lookup is case-sensitive"""
    # Correct case
    response = await client.get("/api/doctor_categories/kardiologiya")
    assert response.status_code == 200
    
    # Wrong case (should not find)
    response = await client.get("/api/doctor_categories/Kardiologiya")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_multiple_categories_by_slug(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test getting different categories by slug"""
    slugs = ["kardiologiya", "nevrologiya", "pediatriya"]
    
    for slug in slugs:
        response = await client.get(f"/api/doctor_categories/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug


# ==========================================
# GET /search - Search Categories
# ==========================================

@pytest.mark.asyncio
async def test_search_categories_by_title(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test searching categories by title"""
    response = await client.get("/api/doctor_categories/search?keyword=Kardio")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 1
    # Should find "Kardiologiya"
    assert any(c["title"] == "Kardiologiya" for c in data)


@pytest.mark.asyncio
async def test_search_categories_by_keyword(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test searching categories by keywords field"""
    response = await client.get("/api/doctor_categories/search?keyword=ürək")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 1
    # Should find "Kardiologiya" (has "ürək" in keywords)
    assert any(c["slug"] == "kardiologiya" for c in data)


@pytest.mark.asyncio
async def test_search_categories_case_insensitive(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that search is case-insensitive"""
    # Lowercase
    response1 = await client.get("/api/doctor_categories/search?keyword=kardio")
    # Uppercase
    response2 = await client.get("/api/doctor_categories/search?keyword=KARDIO")
    # Mixed case
    response3 = await client.get("/api/doctor_categories/search?keyword=KaRdIo")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    
    # All should return same results
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    
    assert len(data1) == len(data2) == len(data3)


@pytest.mark.asyncio
async def test_search_categories_no_results(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test search with no matching results"""
    response = await client.get("/api/doctor_categories/search?keyword=xyz123")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_categories_minimum_length_validation(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that search keyword requires minimum 2 characters"""
    # 1 character (should fail)
    response = await client.get("/api/doctor_categories/search?keyword=k")
    assert response.status_code == 422
    
    # 2 characters (should pass)
    response = await client.get("/api/doctor_categories/search?keyword=ka")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_categories_missing_keyword(client: AsyncClient):
    """Test search without keyword parameter"""
    response = await client.get("/api/doctor_categories/search")
    
    # Should return 422 (validation error)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_categories_partial_match(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that search works with partial matches"""
    response = await client.get("/api/doctor_categories/search?keyword=log")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should find: Kardiologiya, Nevrologiya, Oftalmologiya
    assert len(data) >= 3
    found_slugs = {c["slug"] for c in data}
    assert "kardiologiya" in found_slugs
    assert "nevrologiya" in found_slugs
    assert "oftalmologiya" in found_slugs


@pytest.mark.asyncio
async def test_search_categories_returns_full_data(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that search returns complete category data (not partial)"""
    response = await client.get("/api/doctor_categories/search?keyword=kardio")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check first result has all fields
    if len(data) > 0:
        first_result = data[0]
        assert "id" in first_result
        assert "title" in first_result
        assert "slug" in first_result
        assert "keywords" in first_result
        assert "image" in first_result
        assert "created_at" in first_result
        assert "updated_at" in first_result


# ==========================================
# Edge Cases & Data Validation
# ==========================================

@pytest.mark.asyncio
async def test_get_category_with_special_characters_in_slug(
    client: AsyncClient,
    session
):
    """Test handling of special characters in slug"""
    from models.doctor_category import DoctorCategory
    from datetime import datetime, timezone
    
    # Create category with special slug
    category = DoctorCategory(
        title="Test Category",
        slug="test-category-123",
        keywords="test",
        image="test.jpg",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(category)
    await session.commit()
    
    response = await client.get("/api/doctor_categories/test-category-123")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_with_unicode_characters(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test search with Azerbaijani characters"""
    response = await client.get("/api/doctor_categories/search?keyword=uşaq")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should find "Pediatriya" (has "uşaq" in keywords)
    assert any(c["slug"] == "pediatriya" for c in data)


@pytest.mark.asyncio
async def test_get_all_categories_order(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that categories are returned in consistent order"""
    response1 = await client.get("/api/doctor_categories/")
    response2 = await client.get("/api/doctor_categories/")
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Order should be consistent between calls
    assert [c["id"] for c in data1] == [c["id"] for c in data2]


# ==========================================
# Performance & Optimization Tests
# ==========================================

@pytest.mark.asyncio
async def test_partial_data_is_actually_smaller(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test that partial endpoint returns less data than full endpoint"""
    # Get partial data
    partial_response = await client.get("/api/doctor_categories/")
    partial_data = partial_response.json()
    
    # Get full data for comparison
    full_response = await client.get("/api/doctor_categories/kardiologiya")
    full_data = full_response.json()
    
    # Partial should have fewer keys
    assert len(partial_data[0].keys()) < len(full_data.keys())


# ==========================================
# Integration Tests
# ==========================================

@pytest.mark.asyncio
async def test_full_workflow_list_search_detail(
    client: AsyncClient,
    sample_doctor_categories: list[DoctorCategory]
):
    """Test complete user workflow: list → search → detail"""
    # 1. List all categories
    list_response = await client.get("/api/doctor_categories/")
    assert list_response.status_code == 200
    categories = list_response.json()
    assert len(categories) > 0
    
    # 2. Search for specific category
    search_response = await client.get("/api/doctor_categories/search?keyword=kardio")
    assert search_response.status_code == 200
    search_results = search_response.json()
    assert len(search_results) > 0
    
    # 3. Get details of found category
    found_slug = search_results[0]["slug"]
    detail_response = await client.get(f"/api/doctor_categories/{found_slug}")
    assert detail_response.status_code == 200
    detail_data = detail_response.json()
    assert detail_data["slug"] == found_slug