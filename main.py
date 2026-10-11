from fastapi import FastAPI

from api import articles, health, sections

app = FastAPI()

app.include_router(health.router)
app.include_router(articles.router)
app.include_router(sections.router)
