import pytest
from httpx import AsyncClient

from models.blog import Blog

# ==================== CREATE TESTS ====================


@pytest.mark.asyncio
async def test_create_blog(admin_client: AsyncClient):
    """Yeni blog yarat"""
    blog_data = {
        "title": "Test Blog",
        "description": "Test description",
        "text": "Test content here...",
        "keywords": "test, blog",
        "status": True,
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Blog"
    assert data["slug"] == "test-blog"
    assert data["description"] == "Test description"
    assert data["text"] == "Test content here..."
    assert data["keywords"] == "test, blog"
    assert data["status"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_blog_minimal(admin_client: AsyncClient):
    """Minimal məlumatla blog yarat"""
    blog_data = {
        "title": "Minimal Blog",
        "description": "Short desc",
        "text": "Content",
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 201

    data = response.json()
    assert data["slug"] == "minimal-blog"
    assert data["keywords"] is None
    assert data["image"] is None
    assert data["status"] is True  # Default value


@pytest.mark.asyncio
async def test_create_blog_with_custom_slug(admin_client: AsyncClient):
    """Custom slug ilə blog yarat"""
    blog_data = {
        "title": "My Amazing Post",
        "slug": "custom-slug-2024",
        "description": "Description here",
        "text": "Content here",
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 201

    data = response.json()
    assert data["slug"] == "custom-slug-2024"
    assert data["title"] == "My Amazing Post"


@pytest.mark.asyncio
async def test_create_blog_duplicate_title(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Eyni title-la blog yarat (slug conflict həlli)"""
    blog_data = {
        "title": "Python FastAPI",  # Artıq var
        "description": "Another FastAPI tutorial",
        "text": "More content...",
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 201

    data = response.json()
    assert data["slug"] == "python-fastapi-1"  # Avtomatik -1 əlavə olunub
    assert data["title"] == "Python FastAPI"


@pytest.mark.asyncio
async def test_create_blog_multiple_duplicates(admin_client: AsyncClient):
    """Bir neçə dəfə eyni title"""
    blog_data = {
        "title": "Duplicate Test",
        "description": "Test",
        "text": "Test content",
    }

    # İlk blog
    response1 = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response1.status_code == 201
    assert response1.json()["slug"] == "duplicate-test"

    # İkinci blog (eyni title)
    response2 = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response2.status_code == 201
    assert response2.json()["slug"] == "duplicate-test-1"

    # Üçüncü blog (eyni title)
    response3 = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response3.status_code == 201
    assert response3.json()["slug"] == "duplicate-test-2"


@pytest.mark.asyncio
async def test_create_blog_with_azerbaijani_characters(admin_client: AsyncClient):
    """Azərbaycan hərfləri ilə blog"""
    blog_data = {
        "title": "Azərbaycan Dili və Texnologiya",
        "description": "Ş, Ç, Ğ, Ə, Ö, Ü hərfləri",
        "text": "Məzmun burada...",
        "keywords": "azərbaycan, dil, texnologiya",
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Azərbaycan Dili və Texnologiya"
    assert "az-rbaycan" in data["slug"]  # Slugify düzgün işləyir


@pytest.mark.asyncio
async def test_create_blog_missing_required_fields(admin_client: AsyncClient):
    """Məcburi field-lər yoxdur"""
    # Title yoxdur
    response = await admin_client.post(
        "/api/admin/blogs/",
        json={
            "description": "Test",
            "text": "Test",
        },
    )
    assert response.status_code == 422

    # Description yoxdur
    response = await admin_client.post(
        "/api/admin/blogs/",
        json={
            "title": "Test",
            "text": "Test",
        },
    )
    assert response.status_code == 422

    # Text yoxdur
    response = await admin_client.post(
        "/api/admin/blogs/",
        json={
            "title": "Test",
            "description": "Test",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_blog_draft_status(admin_client: AsyncClient):
    """Draft statuslu blog yarat"""
    blog_data = {
        "title": "Draft Blog",
        "description": "Still working on it",
        "text": "Incomplete content...",
        "status": False,  # Draft
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] is False


# ==================== UPDATE TESTS ====================


@pytest.mark.asyncio
async def test_update_blog_full(admin_client: AsyncClient, sample_blogs: list[Blog]):
    """Blog-u tam yenilə"""
    update_data = {
        "title": "Updated Python FastAPI",
        "description": "Completely updated description",
        "text": "New content here...",
        "keywords": "python, fastapi, updated",
        "status": False,
    }

    response = await admin_client.patch(
        "/api/admin/blogs/python-fastapi", json=update_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Python FastAPI"
    assert data["slug"] == "updated-python-fastapi"  # Slug dəyişib
    assert data["description"] == "Completely updated description"
    assert data["text"] == "New content here..."
    assert data["keywords"] == "python, fastapi, updated"
    assert data["status"] is False


@pytest.mark.asyncio
async def test_update_blog_partial_title_only(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Yalnız title update"""
    response = await admin_client.patch(
        "/api/admin/blogs/sqlmodel-guide", json={"title": "Advanced SQLModel Guide"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Advanced SQLModel Guide"
    assert data["slug"] == "advanced-sqlmodel-guide"
    assert data["description"] == "SQLModel ORM tutorial"  # Dəyişməyib


@pytest.mark.asyncio
async def test_update_blog_partial_status_only(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Yalnız status update"""
    response = await admin_client.patch(
        "/api/admin/blogs/async-programming", json={"status": True}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] is True
    assert data["slug"] == "async-programming"  # Dəyişməyib
    assert data["title"] == "Async Programming"  # Dəyişməyib


@pytest.mark.asyncio
async def test_update_blog_partial_keywords(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Yalnız keywords update"""
    response = await admin_client.patch(
        "/api/admin/blogs/python-fastapi",
        json={"keywords": "python, web, api, framework"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["keywords"] == "python, web, api, framework"


@pytest.mark.asyncio
async def test_update_blog_partial_image(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Image əlavə et"""
    response = await admin_client.patch(
        "/api/admin/blogs/sqlmodel-guide", json={"image": "/images/sqlmodel-cover.jpg"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["image"] == "/images/sqlmodel-cover.jpg"


@pytest.mark.asyncio
async def test_update_blog_not_found(admin_client: AsyncClient):
    """Olmayan blog-u yenilə"""
    response = await admin_client.patch(
        "/api/admin/blogs/non-existent-slug", json={"title": "New Title"}
    )
    assert response.status_code == 404

    error = response.json()
    assert "tapılmadı" in error["detail"]


@pytest.mark.asyncio
async def test_update_blog_empty_data(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Boş data ilə update (heç nə dəyişmir)"""
    response = await admin_client.patch("/api/admin/blogs/python-fastapi", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Python FastAPI"  # Dəyişməyib


@pytest.mark.asyncio
async def test_update_blog_slug_conflict(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Title dəyişəndə slug conflict"""
    # "Python FastAPI" artıq var
    response = await admin_client.patch(
        "/api/admin/blogs/sqlmodel-guide", json={"title": "Python FastAPI"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["slug"] == "python-fastapi-1"  # Conflict həll olunub


# ==================== DELETE TESTS ====================


@pytest.mark.asyncio
async def test_delete_blog(admin_client: AsyncClient, sample_blogs: list[Blog]):
    """Blog sil"""
    response = await admin_client.delete("/api/admin/blogs/async-programming")
    assert response.status_code == 200

    data = response.json()
    assert "silindi" in data["message"]
    assert data["deleted_blog"] == "Async Programming"

    # Silinmiş blog-u yoxla
    get_response = await admin_client.get("/api/blogs/async-programming")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_blog_not_found(admin_client: AsyncClient):
    """Olmayan blog-u sil"""
    response = await admin_client.delete("/api/admin/blogs/non-existent")
    assert response.status_code == 404

    error = response.json()
    assert "tapılmadı" in error["detail"]


@pytest.mark.asyncio
async def test_delete_blog_twice(admin_client: AsyncClient, sample_blogs: list[Blog]):
    """Eyni blog-u iki dəfə sil"""
    # İlk dəfə sil
    response1 = await admin_client.delete("/api/admin/blogs/python-fastapi")
    assert response1.status_code == 200

    # İkinci dəfə sil (artıq yoxdur)
    response2 = await admin_client.delete("/api/admin/blogs/python-fastapi")
    assert response2.status_code == 404


# ==================== AUTHORIZATION TESTS ====================


@pytest.mark.asyncio
async def test_admin_create_requires_auth(client: AsyncClient):
    """Admin auth olmadan create"""
    blog_data = {
        "title": "Test",
        "description": "Test",
        "text": "Test",
    }

    response = await client.post("/api/admin/blogs/", json=blog_data)
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_admin_update_requires_auth(
    client: AsyncClient, sample_blogs: list[Blog]
):
    """Admin auth olmadan update"""
    response = await client.patch(
        "/api/admin/blogs/python-fastapi", json={"title": "New Title"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_delete_requires_auth(
    client: AsyncClient, sample_blogs: list[Blog]
):
    """Admin auth olmadan delete"""
    response = await client.delete("/api/admin/blogs/python-fastapi")
    assert response.status_code == 403


# ==================== LIFECYCLE TESTS ====================


@pytest.mark.asyncio
async def test_full_blog_lifecycle(admin_client: AsyncClient):
    """Tam blog lifecycle: Create → Read → Update → Delete"""

    # 1. Create
    create_data = {
        "title": "Lifecycle Test Blog",
        "description": "Testing full lifecycle",
        "text": "Initial content here...",
        "keywords": "test, lifecycle",
        "status": False,  # Draft
    }

    create_response = await admin_client.post("/api/admin/blogs/", json=create_data)
    assert create_response.status_code == 201
    created_blog = create_response.json()
    slug = created_blog["slug"]
    blog_id = created_blog["id"]

    assert slug == "lifecycle-test-blog"
    assert created_blog["status"] is False

    # 2. Read
    read_response = await admin_client.get(f"/api/blogs/{slug}")
    assert read_response.status_code == 200
    read_blog = read_response.json()
    assert read_blog["id"] == blog_id
    assert read_blog["title"] == "Lifecycle Test Blog"

    # 3. Update - Publish
    update_response = await admin_client.patch(
        f"/api/admin/blogs/{slug}", json={"status": True, "text": "Updated content"}
    )
    assert update_response.status_code == 200
    updated_blog = update_response.json()
    assert updated_blog["status"] is True
    assert updated_blog["text"] == "Updated content"

    # 4. Delete
    delete_response = await admin_client.delete(f"/api/admin/blogs/{slug}")
    assert delete_response.status_code == 200

    # 5. Verify deleted
    verify_response = await admin_client.get(f"/api/blogs/{slug}")
    assert verify_response.status_code == 404


@pytest.mark.asyncio
async def test_multiple_blogs_operations(admin_client: AsyncClient):
    """Bir neçə blog ilə əməliyyatlar"""

    # 3 blog yarat
    blogs = []
    for i in range(1, 4):
        response = await admin_client.post(
            "/api/admin/blogs/",
            json={
                "title": f"Test Blog {i}",
                "description": f"Description {i}",
                "text": f"Content {i}",
            },
        )
        assert response.status_code == 201
        blogs.append(response.json())

    # Hamısını list-lə
    list_response = await admin_client.get("/api/blogs/")
    assert list_response.status_code == 200
    all_blogs = list_response.json()
    assert len(all_blogs) >= 3

    # Birini update et
    update_response = await admin_client.patch(
        f"/api/admin/blogs/{blogs[1]['slug']}", json={"status": False}
    )
    assert update_response.status_code == 200

    # Birini sil
    delete_response = await admin_client.delete(f"/api/admin/blogs/{blogs[2]['slug']}")
    assert delete_response.status_code == 200

    # Yoxla
    verify_response = await admin_client.get(f"/api/blogs/{blogs[2]['slug']}")
    assert verify_response.status_code == 404


# ==================== EDGE CASES ====================


@pytest.mark.asyncio
async def test_create_blog_very_long_title(admin_client: AsyncClient):
    """Çox uzun title"""
    long_title = "A" * 300  # 300 simvol

    blog_data = {
        "title": long_title,
        "description": "Test",
        "text": "Test",
    }

    response = await admin_client.post("/api/admin/blogs/", json=blog_data)
    # Model max_length=255 varsa 422, yoxsa 201
    assert response.status_code in [201, 422]


@pytest.mark.asyncio
async def test_update_blog_clear_optional_fields(
    admin_client: AsyncClient, sample_blogs: list[Blog]
):
    """Optional field-ləri təmizlə"""
    response = await admin_client.patch(
        "/api/admin/blogs/python-fastapi", json={"keywords": None, "image": None}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["keywords"] is None
    assert data["image"] is None
