from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Financial Notes Generator API")
app.include_router(router) 