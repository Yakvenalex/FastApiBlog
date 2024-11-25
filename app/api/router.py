from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from app.api.schemas import BlogCreateSchemaBase, BlogCreateSchemaAdd, BlogFullResponse, BlogNotFind
from app.auth.dependencies import get_current_user, get_blog_info
from app.auth.models import User
from app.dao.session_maker import SessionDep, TransactionSessionDep
from app.api.dao import BlogDAO, BlogTagDAO, TagDAO

router = APIRouter(prefix='/api', tags=['API'])


@router.delete('/delete_blog/{blog_id}', summary="Удалить блог")
async def delete_blog(
        blog_id: int,
        session: AsyncSession = TransactionSessionDep,
        current_user: User = Depends(get_current_user)
):
    result = await BlogDAO.delete_blog(session, blog_id, current_user.id)
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['message'])
    return result


@router.patch('/change_blog_status/{blog_id}', summary="Изменить статус блога")
async def change_blog_status(
        blog_id: int,
        new_status: str,
        session: AsyncSession = TransactionSessionDep,
        current_user: User = Depends(get_current_user)
):
    result = await BlogDAO.change_blog_status(session, blog_id, new_status, current_user.id)
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['message'])
    return result


@router.post("/add_post/", summary="Добавление нового блога с тегами")
async def add_blog(
        add_data: BlogCreateSchemaBase,
        user_data: User = Depends(get_current_user),
        session: AsyncSession = TransactionSessionDep
):
    blog_dict = add_data.model_dump()
    blog_dict['author'] = user_data.id
    tags = blog_dict.pop('tags', [])

    try:
        blog = await BlogDAO.add(session=session, values=BlogCreateSchemaAdd.model_validate(blog_dict))
        blog_id = blog.id

        if tags:
            tags_ids = await TagDAO.add_tags(session=session, tag_names=tags)
            await BlogTagDAO.add_blog_tags(session=session,
                                           blog_tag_pairs=[{'blog_id': blog_id, 'tag_id': i} for i in tags_ids])

        return {'status': 'success', 'message': f'Блог с ID {blog_id} успешно добавлен с тегами.'}
    except IntegrityError as e:
        if "UNIQUE constraint failed" in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Блог с таким заголовком уже существует.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при добавлении блога.")


@router.get('/get_blog/{blog_id}', summary="Получить информацию по блогу")
async def get_blog_endpoint(
        blog_id: int,
        blog_info: BlogFullResponse | BlogNotFind = Depends(get_blog_info)
) -> BlogFullResponse | BlogNotFind:
    return blog_info


@router.get('/blogs/', summary="Получить все блоги в статусе 'publish'")
async def get_blog_info(
        author_id: int | None = None,
        tag: str | None = None,
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(10, ge=10, le=100, description="Записей на странице"),
        session: AsyncSession = SessionDep,
):
    try:
        result = await BlogDAO.get_blog_list(session=session, author_id=author_id, tag=tag, page=page,
                                             page_size=page_size)
        return result if result['blogs'] else BlogNotFind(message="Блоги не найдены", status='error')
    except Exception as e:
        logger.error(f"Ошибка при получении блогов: {e}")
        return JSONResponse(status_code=500, content={"detail": "Ошибка сервера"})
