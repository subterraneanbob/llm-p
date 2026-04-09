from fastapi import FastAPI

from app.api import routes_auth
from app.api.deps import lifespan
from app.core.config import settings


app = FastAPI(lifespan=lifespan)
app.include_router(routes_auth.router)


@app.get("/health")
async def health():
    return {"status": "OK", "env": settings.env}
