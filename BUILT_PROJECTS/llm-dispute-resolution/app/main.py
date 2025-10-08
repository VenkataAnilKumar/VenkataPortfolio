from fastapi import FastAPI
from .api.routers.disputes import router as disputes_router
from .infra.db import init_db
from .telemetry.metrics import metrics_router

app = FastAPI(title="Dispute Resolution API", version="0.1.0")

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(disputes_router, prefix="/v1")
app.include_router(metrics_router, prefix="/v1")

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}
