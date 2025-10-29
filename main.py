from fastapi import FastAPI
from core.database import Base, engine
from api.endpoints import items

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(items.router, prefix="/items", tags=["items"])
