import better_exceptions

from fastapi import FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse, Response

from app.db import ActiveSession
from app.routers.user import router as user_router

better_exceptions.MAX_LENGTH = None

description = """
Staket API helps you do awesome stuff. 🚀
"""
app = FastAPI(
    title="staket API",
    description=description,
    version="0.0.1",
    terms_of_service="https://github.com/tugrulcan/staket/blob/main/LICENSE",
    contact={
        "name": "Tugrul Can Söllü",
        "url": "https://www.linkedin.com/in/tugrulcan/",
        "email": "tugrulcansollu+staketapi@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/tugrulcan/staket/blob/main/LICENSE",
    },
    redoc_url=None,
)

app.include_router(user_router)


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/db_ready")
async def check_db_readiness(
    session: AsyncSession = ActiveSession,
) -> Response:
    if session.is_active:
        return Response(
            status_code=status.HTTP_200_OK,
            content="Database is ready.",
        )
    else:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not ready.",
        )
