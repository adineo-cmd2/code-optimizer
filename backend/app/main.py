from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
import app.models.user  # noqa: F401
import app.models.optimization_session  # noqa: F401
import app.models.bottleneck_record  # noqa: F401
import app.models.optimized_variant  # noqa: F401
from app.api.routes import history, optimize

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Code Optimizer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4328"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(history.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
