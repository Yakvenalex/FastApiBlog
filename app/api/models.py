from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from app.dao.database import Base, str_uniq


# Промежуточная таблица для связи Many-to-Many
class BlogTag(Base):
    __tablename__ = 'blog_tags'

    # Внешние ключи
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    # Уникальное ограничение для пары blog_id и tag_id
    __table_args__ = (
        UniqueConstraint('blog_id', 'tag_id', name='uq_blog_tag'),
    )


class Blog(Base):
    # Заголовок статьи
    title: Mapped[str_uniq]

    # Автор (внешний ключ на таблицу Users)
    author: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Ссылка на объект пользователя
    user: Mapped["User"] = relationship("User", back_populates="blogs")

    # Содержание статьи в формате Markdown
    content: Mapped[str] = mapped_column(Text)

    short_description: Mapped[str] = mapped_column(Text)

    # Статус статьи
    status: Mapped[str] = mapped_column(default="published", server_default='published')

    # Связь Many-to-Many с тегами
    tags: Mapped[list["Tag"]] = relationship(
        secondary="blog_tags",  # Указываем промежуточную таблицу
        back_populates="blogs"
    )


class Tag(Base):
    # Название тега
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Связь Many-to-Many с блогами
    blogs: Mapped[list["Blog"]] = relationship(
        secondary="blog_tags",  # Указываем промежуточную таблицу
        back_populates="tags"
    )
