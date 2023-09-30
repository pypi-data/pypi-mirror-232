from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiconsole.api.routers import app_router
from aiconsole.settings import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router)