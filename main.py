from fastapi import FastAPI
from routers import query_handler

app = FastAPI()
app.include_router(query_handler.router, prefix="/api/v1")
