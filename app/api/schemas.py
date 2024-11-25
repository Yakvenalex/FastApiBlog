from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, computed_field, Field


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BlogCreateSchemaBase(BaseModelConfig):
    title: str
    content: str
    short_description: str
    tags: List[str] = []


class BlogCreateSchemaAdd(BlogCreateSchemaBase):
    author: int


class UserBase(BaseModelConfig):
    id: int
    first_name: str
    last_name: str


class TagResponse(BaseModelConfig):
    id: int
    name: str


class BlogFullResponse(BaseModelConfig):
    id: int
    author: int
    title: str
    content: str
    short_description: str
    created_at: datetime
    status: str
    tags: List[TagResponse]
    # Это поле нужно для работы computed fields, но оно не будет включено в финальный JSON
    user: UserBase = Field(exclude=True)

    # Используем вычисляемые поля для преобразования данных о пользователе
    @computed_field
    @property
    def author_id(self) -> int:
        return self.user.id if self.user else None

    @computed_field
    @property
    def author_name(self) -> str:
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return None


class BlogNotFind(BaseModel):
    message: str
    status: str
