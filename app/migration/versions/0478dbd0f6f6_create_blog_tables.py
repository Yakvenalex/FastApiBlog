"""create blog tables

Revision ID: 0478dbd0f6f6
Revises: 00c67b7a5799
Create Date: 2024-11-22 11:10:32.769648
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0478dbd0f6f6'
down_revision: Union[str, None] = '00c67b7a5799'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создание таблицы tags
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('name', sa.String(length=50), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )

    # Создание таблицы blogs
    op.create_table(
        'blogs',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False, unique=True),
        sa.Column('author', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )

    # Создание таблицы blog_tags
    op.create_table(
        'blog_tags',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('blog_id', sa.Integer(), sa.ForeignKey('blogs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.UniqueConstraint('blog_id', 'tag_id', name='uq_blog_tag')
    )


def downgrade() -> None:
    # Удаление таблиц в обратном порядке зависимости
    op.drop_table('blog_tags')
    op.drop_table('blogs')
    op.drop_table('tags')
