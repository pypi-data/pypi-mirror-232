from fastapi import APIRouter

from aiconsole.api.endpoints.analyse import router as analyse_router
from aiconsole.api.endpoints.execute import router as execute_router

app_router = APIRouter()

app_router.include_router(analyse_router, tags=["analyse"])
app_router.include_router(execute_router, tags=["execute"])
