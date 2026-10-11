from fastapi import APIRouter
from sqlmodel import text

from api.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: SessionDep):
    session.exec(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
