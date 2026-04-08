from fastapi import FastAPI

from app.api.deps import lifespan
from app.api import routes_auth


app = FastAPI(lifespan=lifespan)
app.include_router(routes_auth.router)


@app.get("/health")
async def health():
    return {"status": "OK"}
