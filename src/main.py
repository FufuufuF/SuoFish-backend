from fastapi import FastAPI
from src.api.v1.api import router as v1_router
from src.db.session import Base, engine
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(v1_router, prefix="/api/v1")