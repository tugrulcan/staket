from typing import Dict

import better_exceptions

from fastapi import FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db import ActiveSession

better_exceptions.MAX_LENGTH = None

description = """
Stacket API helps you do awesome stuff. 🚀
"""
app = FastAPI(
    title="Stacket API",
    description=description,
    version="0.0.1",
    terms_of_service="https://github.com/tugrulcan/staket/blob/main/LICENSE",
    contact={
        "name": "Tugrul Can Söllü",
        "url": "https://www.linkedin.com/in/tugrulcan/",
        "email": "tugrulcansollu+stacketapi@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/tugrulcan/staket/blob/main/LICENSE",
    },
    redoc_url=None,
)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello, World!"}


@app.get("/hello/{name}")
async def say_hello(name: str) -> Dict[str, str]:
    return {"message": f"Hello {name}"}


@app.get("/db_ready")
async def check_db_readiness(
    session: Session = ActiveSession,
) -> Response:
    if session.is_active:
        return Response(
            status_code=status.HTTP_200_OK,
            content="Database is ready.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is not ready.",
        )
