from typing import Dict

from fastapi import FastAPI

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
