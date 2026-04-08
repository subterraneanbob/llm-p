from fastapi import FastAPI

from app.api.deps import lifespan


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "OK"}
