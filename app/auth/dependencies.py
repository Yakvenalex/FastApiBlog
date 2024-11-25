from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dao import BlogDAO
from app.api.schemas import BlogFullResponse, BlogNotFind
from app.config import settings
from app.exceptions import TokenExpiredException, NoJwtException, NoUserIdException, ForbiddenException, TokenNoFound
from app.auth.dao import UsersDAO
from app.auth.models import User
from app.dao.session_maker import SessionDep


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise TokenNoFound
    return token


async def get_current_user(token: str = Depends(get_token), session: AsyncSession = SessionDep):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except JWTError:
        raise NoJwtException

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise TokenExpiredException

    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException

    user = await UsersDAO.find_one_or_none_by_id(data_id=int(user_id), session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return user


def get_token_optional(request: Request) -> str | None:
    return request.cookies.get('users_access_token')


async def get_current_user_optional(
        token: str | None = Depends(get_token_optional),
        session: AsyncSession = SessionDep
) -> User | None:
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except JWTError:
        return None

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        return None

    user_id: str = payload.get('sub')
    if not user_id:
        return None

    user = await UsersDAO.find_one_or_none_by_id(data_id=int(user_id), session=session)
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role.id in [3, 4]:
        return current_user
    raise ForbiddenException


async def get_blog_info(
        blog_id: int,
        session: AsyncSession = SessionDep,
        user_data: User | None = Depends(get_current_user_optional)
) -> BlogFullResponse | BlogNotFind:
    author_id = user_data.id if user_data else None
    return await BlogDAO.get_full_blog_info(session=session, blog_id=blog_id, author_id=author_id)
