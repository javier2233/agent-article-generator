import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from api.deps import SessionDep
from models import Article, ArticleCreate, ArticleRead, ArticleUpdate, Section

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("", response_model=ArticleRead, status_code=201)
def create_article(article: ArticleCreate, session: SessionDep):
    if article.section_id and not session.get(Section, article.section_id):
        raise HTTPException(status_code=422, detail="Section not found")
    db_article = Article.model_validate(article)
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article


@router.get("", response_model=list[ArticleRead])
def list_articles(session: SessionDep, offset: int = 0, limit: int = 100):
    return session.exec(select(Article).offset(offset).limit(limit)).all()


@router.get("/{article_id}", response_model=ArticleRead)
def get_article(article_id: uuid.UUID, session: SessionDep):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.patch("/{article_id}", response_model=ArticleRead)
def update_article(article_id: uuid.UUID, article: ArticleUpdate, session: SessionDep):
    db_article = session.get(Article, article_id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    if article.section_id and not session.get(Section, article.section_id):
        raise HTTPException(status_code=422, detail="Section not found")
    db_article.sqlmodel_update(article.model_dump(exclude_unset=True))
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article


@router.delete("/{article_id}", status_code=204)
def delete_article(article_id: uuid.UUID, session: SessionDep):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    session.delete(article)
    session.commit()
