import pytest
from httpx import AsyncClient

from models.blog import Blog


@pytest.mark.asyncio
async def test_get_all_blogs_empty(client: AsyncClient):
    """Heç blog olmayan halda"""
    response = await client.get("/api/blogs/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_blogs(client: AsyncClient, sample_blogs: list[Blog]):
    """Bütün blogları gətir"""
    response = await client.get("/api/blogs/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["slug"] == "python-fastapi"
    assert "created_at" in data[0]
    assert "id" in data[0]


@pytest.mark.asyncio
async def test_get_all_blogs_pagination(client: AsyncClient, sample_blogs: list[Blog]):
    """Pagination test"""
    response = await client.get("/api/blogs/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["slug"] == "sqlmodel-guide"


@pytest.mark.asyncio
async def test_get_blog_by_slug(client: AsyncClient, sample_blogs: list[Blog]):
    """Slug-a görə blog tap"""
    response = await client.get("/api/blogs/python-fastapi")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Python FastAPI"
    assert data["slug"] == "python-fastapi"
    assert data["keywords"] == "python, fastapi, web"
    assert data["description"] == "FastAPI tutorial"


@pytest.mark.asyncio
async def test_get_blog_not_found(client: AsyncClient):
    """Olmayan blog"""
    response = await client.get("/api/blogs/non-existent")
    assert response.status_code == 404
    error = response.json()
    assert "tapılmadı" in error["detail"]


@pytest.mark.asyncio
async def test_search_blogs(client: AsyncClient, sample_blogs: list[Blog]):
    """Blog axtarışı"""
    response = await client.get("/api/blogs/search?q=python")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # "Python FastAPI" və "Async Programming"

    # Title-də "python" olan bloglar
    titles = [blog["title"] for blog in data]
    assert "Python FastAPI" in titles
    assert "Async Programming" in titles


@pytest.mark.asyncio
async def test_search_blogs_case_insensitive(
    client: AsyncClient, sample_blogs: list[Blog]
):
    """Case-insensitive axtarış"""
    response = await client.get("/api/blogs/search?q=PYTHON")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_search_blogs_no_results(client: AsyncClient, sample_blogs: list[Blog]):
    """Axtarış nəticəsi yoxdur"""
    response = await client.get("/api/blogs/search?q=javascript")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_blogs_short_query(client: AsyncClient):
    """Qısa axtarış sorğusu (validation error)"""
    response = await client.get("/api/blogs/search?q=p")
    assert response.status_code == 422
    error = response.json()

    # detail list-dir, ilk elementi götür
    assert isinstance(error["detail"], list)
    assert len(error["detail"]) > 0

    first_error = error["detail"][0]
    assert "2 characters" in first_error["msg"]


@pytest.mark.asyncio
async def test_search_blogs_missing_query(client: AsyncClient):
    """Axtarış sorğusu yoxdur"""
    response = await client.get("/api/blogs/search")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_pagination_limits(client: AsyncClient, sample_blogs: list[Blog]):
    """Pagination limit yoxlaması"""
    # Skip beyond available items
    response = await client.get("/api/blogs/?skip=10&limit=10")
    assert response.status_code == 200
    assert response.json() == []

    # Limit 0
    response = await client.get("/api/blogs/?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_search_in_description(client: AsyncClient, sample_blogs: list[Blog]):
    """Description-da axtarış"""
    response = await client.get("/api/blogs/search?q=tutorial")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # FastAPI və SQLModel tutorial
