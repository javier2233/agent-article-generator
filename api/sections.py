import uuid

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from api.deps import SessionDep
from models import Article, ArticleRead, Section, SectionCreate, SectionRead, SectionUpdate

router = APIRouter(prefix="/sections", tags=["sections"])


@router.post("", response_model=SectionRead, status_code=201)
def create_section(section: SectionCreate, session: SessionDep):
    db_section = Section.model_validate(section)
    session.add(db_section)
    session.commit()
    session.refresh(db_section)
    return db_section


@router.get("", response_model=list[SectionRead])
def list_sections(session: SessionDep, offset: int = 0, limit: int = 100):
    return session.exec(select(Section).offset(offset).limit(limit)).all()


@router.get("/{section_id}", response_model=SectionRead)
def get_section(section_id: uuid.UUID, session: SessionDep):
    section = session.get(Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@router.patch("/{section_id}", response_model=SectionRead)
def update_section(section_id: uuid.UUID, section: SectionUpdate, session: SessionDep):
    db_section = session.get(Section, section_id)
    if not db_section:
        raise HTTPException(status_code=404, detail="Section not found")
    db_section.sqlmodel_update(section.model_dump(exclude_unset=True))
    session.add(db_section)
    session.commit()
    session.refresh(db_section)
    return db_section


@router.delete("/{section_id}", status_code=204)
def delete_section(section_id: uuid.UUID, session: SessionDep):
    section = session.get(Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    session.delete(section)
    session.commit()


@router.get("/{section_id}/articles", response_model=list[ArticleRead])
def list_section_articles(
    section_id: uuid.UUID, session: SessionDep, offset: int = 0, limit: int = 100
):
    if not session.get(Section, section_id):
        raise HTTPException(status_code=404, detail="Section not found")
    statement = (
        select(Article).where(Article.section_id == section_id).offset(offset).limit(limit)
    )
    return session.exec(statement).all()
