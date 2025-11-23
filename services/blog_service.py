
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from repositories.blog_repository import BlogRepository
from schemas import BlogCreate, BlogResponse, BlogUpdate


class BlogService:
    """
    Blog əməliyyatları üçün service layer.

    Bu class yalnız stateless utility funksiyalar saxlayır.
    Repository ilə router arasında "Business Logic" körpüsüdür.
    """

    # --------------------------------------------
    # CREATE
    # --------------------------------------------
    @staticmethod
    async def create_blog(db: AsyncSession, blog_data: BlogCreate) -> BlogResponse:
        """
        Yeni blog yarat.

        Args:
            db (AsyncSession): Database session
            blog_data (BlogCreate): Blog məlumatları

        Returns:
            BlogResponse: Yaradıln blog məlumatları

        Raises:
            HTTPException: Yaratma zamanı xəta olarsa
        """
        try:
            blog = await BlogRepository.create(db, blog_data)
            return BlogResponse.model_validate(blog)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Blog yaradıla bilmədi: {str(e)}",
            )

    # --------------------------------------------
    # GET ALL
    # --------------------------------------------
    @staticmethod
    async def get_all_blogs(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[BlogResponse]:
        """
        Bütün blogları gətir.

        Args:
            db (AsyncSession)
            skip (int): Neçə elementi keçmək
            limit (int): Maksimum neçə nəticə

        Returns:
            list[BlogResponse]: Blog siyahısı
        """
        blogs = await BlogRepository.get_all(db, skip, limit)
        return [BlogResponse.model_validate(blog) for blog in blogs]

    # --------------------------------------------
    # GET BY SLUG
    # --------------------------------------------
    @staticmethod
    async def get_blog(db: AsyncSession, slug: str) -> BlogResponse:
        """
        Slug-a görə tək blog gətir.

        Args:
            db (AsyncSession)
            slug (str): Blog-un slug-ı

        Returns:
            BlogResponse: Blog məlumatı

        Raises:
            HTTPException: Blog tapılmadıqda
        """
        blog = await BlogRepository.get_by_slug(db, slug)
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{slug}' slug-lu blog tapılmadı",
            )
        return BlogResponse.model_validate(blog)

    # --------------------------------------------
    # UPDATE
    # --------------------------------------------
    @staticmethod
    async def update_blog(
        db: AsyncSession, slug: str, blog_data: BlogUpdate
    ) -> BlogResponse:
        """
        Blog yenilə.

        Args:
            db (AsyncSession)
            slug (str): Yenilənəcək blog slug-ı
            blog_data (BlogUpdate): Yeni məlumatlar

        Returns:
            BlogResponse: Yenilənmiş blog

        Raises:
            HTTPException: Blog tapılmazsa
        """
        blog = await BlogRepository.update(db, slug, blog_data)
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{slug}' slug-lu blog tapılmadı",
            )
        return BlogResponse.model_validate(blog)

    # --------------------------------------------
    # DELETE
    # --------------------------------------------
    @staticmethod
    async def delete_blog(db: AsyncSession, slug: str) -> dict:
        """
        Blog sil.

        Args:
            db (AsyncSession)
            slug (str): Silinəcək blog slug-ı

        Returns:
            dict: Silmə nəticəsi

        Raises:
            HTTPException: Blog tapılmazsa
        """
        blog = await BlogRepository.delete(db, slug)
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"'{slug}' slug-lu blog tapılmadı",
            )
        return {
            "message": f"'{slug}' slug-lu blog silindi",
            "deleted_blog": blog.title,
        }

    # --------------------------------------------
    # SEARCH
    # --------------------------------------------
    @staticmethod
    async def search_blogs(
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[BlogResponse]:
        """
        Axtarış əsasında blogları gətir.

        Args:
            db (AsyncSession)
            query (str): Axtarış sorğusu
            skip (int)
            limit (int)

        Returns:
            list[BlogResponse]: Axtarışa uyğun bloglar

        Raises:
            HTTPException: Sorğu çox qısadırsa
        """
        if not query or len(query) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Axtarış üçün ən azı 2 simvol daxil edin",
            )

        blogs = await BlogRepository.search(db, query, skip, limit)
        return [BlogResponse.model_validate(blog) for blog in blogs]

