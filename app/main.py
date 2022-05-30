from fastapi import FastAPI

app = FastAPI()  # pragma: no cover


@app.get("/")
async def read_root() -> str:  # pragma: no cover
    return "Hello, World!"
