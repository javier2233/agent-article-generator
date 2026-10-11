import uuid
from datetime import datetime, timezone

from pydantic import field_validator
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


class SectionBase(SQLModel):
    title: str = Field(max_length=255)


class Section(SectionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    articles: list["Article"] = Relationship(back_populates="section")


class SectionCreate(SectionBase):
    pass


class SectionRead(SectionBase):
    id: uuid.UUID


class SectionUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)

    @field_validator("title")
    @classmethod
    def title_not_null(cls, value: str | None) -> str:
        # Omitir el campo es válido (no se modifica); enviarlo como null no.
        if value is None:
            raise ValueError("title cannot be null")
        return value


class ArticleBase(SQLModel):
    title: str = Field(max_length=255)
    content: str
    section_id: uuid.UUID | None = Field(
        default=None, foreign_key="section.id", index=True, ondelete="SET NULL"
    )


class Article(ArticleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    section: Section | None = Relationship(back_populates="articles")


class ArticleCreate(ArticleBase):
    pass


class ArticlePredictionCreate(SQLModel):
    home_team: str = Field(min_length=1, max_length=100)
    away_team: str = Field(min_length=1, max_length=100)
    competition: str | None = Field(default=None, max_length=100)
    section_id: uuid.UUID | None = None


class ArticleRead(ArticleBase):
    id: uuid.UUID
    created_at: datetime


class ArticleUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    content: str | None = None
    # null es válido: quita el artículo de su sección.
    section_id: uuid.UUID | None = None

    @field_validator("title", "content")
    @classmethod
    def not_null(cls, value: str | None) -> str:
        # Omitir el campo es válido (no se modifica); enviarlo como null no.
        if value is None:
            raise ValueError("cannot be null")
        return value
