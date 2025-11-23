from typing import Optional, Sequence

from slugify import slugify
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.blog import Blog
from schemas import BlogCreate, BlogUpdate


class BlogRepository:
    """
    Blog məlumatlarının idarə olunması üçün Repository Layer.
    """

    # -------------------------
    # Utility: Slug generator
    # -------------------------
    @staticmethod
    async def _generate_unique_slug(db: AsyncSession, base_slug: str) -> str:
        """Slug unikal deyilsə, sonuna -1, -2 əlavə edib yenisini yaradır."""
        slug = base_slug
        counter = 1

        stmt = select(Blog).where(Blog.slug == slug)
        result = await db.exec(stmt)
        exists = result.first()

        while exists:
            slug = f"{base_slug}-{counter}"
            stmt = select(Blog).where(Blog.slug == slug)
            result = await db.exec(stmt)
            exists = result.first()
            counter += 1

        return slug

    # -------------------------
    # SELECT OPERATIONS
    # -------------------------
    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Blog]:
        """Slug-a görə blog gətir."""
        stmt = select(Blog).where(Blog.slug == slug)
        result = await db.exec(stmt)
        return result.first()

    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Blog]:
        """Bütün bloglar."""
        stmt = select(Blog).offset(skip).limit(limit)
        result = await db.exec(stmt)
        return result.all()

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    async def create(db: AsyncSession, blog_data: BlogCreate) -> Blog:
        """Yeni blog yarat."""

        base_slug = blog_data.slug or slugify(blog_data.title)
        slug = await BlogRepository._generate_unique_slug(db, base_slug)

        blog = Blog(
            title=blog_data.title,
            slug=slug,
            description=blog_data.description,
            text=blog_data.text,
            keywords=blog_data.keywords,
            image=blog_data.image,
            status=blog_data.status,
        )

        db.add(blog)
        await db.commit()
        await db.refresh(blog)
        return blog

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    async def update(
        db: AsyncSession, slug: str, blog_data: BlogUpdate
    ) -> Optional[Blog]:
        blog = await BlogRepository.get_by_slug(db, slug)
        if not blog:
            return None

        update_data = blog_data.model_dump(exclude_unset=True)

        # Title dəyişirsə slug da yenilənməlidir
        if "title" in update_data:
            new_base_slug = slugify(update_data["title"])
            new_slug = await BlogRepository._generate_unique_slug(db, new_base_slug)
            update_data["slug"] = new_slug

        for key, value in update_data.items():
            setattr(blog, key, value)

        db.add(blog)
        await db.commit()
        await db.refresh(blog)
        return blog

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    async def delete(db: AsyncSession, slug: str) -> Optional[Blog]:
        """Blog-u sil."""
        blog = await BlogRepository.get_by_slug(db, slug)
        if not blog:
            return None

        await db.delete(blog)
        await db.commit()
        return blog

    # -------------------------
    # SEARCH
    # -------------------------
    @staticmethod
    async def search(
        db: AsyncSession, query: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Blog]:
        from sqlmodel import col, or_

        search_term = f"%{query.lower()}%"

        stmt = (
            select(Blog)
            .where(
                or_(
                    col(Blog.title).ilike(search_term),
                    col(Blog.description).ilike(search_term),
                    col(Blog.keywords).ilike(search_term),
                )
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.exec(stmt)
        return result.all()

