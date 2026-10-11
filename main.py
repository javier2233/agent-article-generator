from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select, text

from db import get_session
from models import Article, ArticleCreate, ArticleRead

app = FastAPI()

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/health")
def health(session: SessionDep):
    session.exec(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@app.post("/articles", response_model=ArticleRead, status_code=201)
def create_article(article: ArticleCreate, session: SessionDep):
    db_article = Article.model_validate(article)
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article


@app.get("/articles", response_model=list[ArticleRead])
def list_articles(session: SessionDep, offset: int = 0, limit: int = 100):
    return session.exec(select(Article).offset(offset).limit(limit)).all()


@app.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, session: SessionDep):
    article = session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
