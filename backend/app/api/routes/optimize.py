from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.optimization_session import OptimizationSession
from app.models.bottleneck_record import BottleneckRecord
from app.models.optimized_variant import OptimizedVariant
from app.models.user import User
from app.schemas.optimize import (
    OptimizeApplyIn,
    OptimizeDiffOut,
    OptimizeSessionOut,
    OptimizeSubmitIn,
    OptimizeSubmitOut,
)
from app.services import optimize_pipeline as pipeline
from app.services import tradeoff_selector as selector
from app.services import diff_service

router = APIRouter()


def _own(db: Session, user: User, sid: int) -> OptimizationSession:
    s = db.query(OptimizationSession).filter(
        OptimizationSession.id == sid,
        OptimizationSession.user_id == user.id,
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


@router.post("/submit", response_model=OptimizeSubmitOut)
def submit(body: OptimizeSubmitIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not (body.code or "").strip():
        raise HTTPException(status_code=400, detail="Code required")
    language = (body.language or "").strip() or "python"
    runtime = {
        "traffic": body.traffic or "",
        "data_volume": body.data_volume or "",
        "input_size": body.input_size or "",
    }
    return pipeline.submit(db, user.id, body.code, language, runtime)


@router.get("/{sid}", response_model=OptimizeSessionOut)
def get_session(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own(db, user, sid)
    bottlenecks = db.query(BottleneckRecord).filter(BottleneckRecord.session_id == s.id).order_by(BottleneckRecord.id).all()
    variants = db.query(OptimizedVariant).filter(OptimizedVariant.session_id == s.id).order_by(OptimizedVariant.id).all()
    return OptimizeSessionOut(
        session_id=s.id,
        language=s.language,
        bottlenecks=bottlenecks,
        variants=variants,
    )


@router.post("/{sid}/apply")
def apply(sid: int, body: OptimizeApplyIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own(db, user, sid)
    kind = selector.select({"speed": body.speed, "memory": body.memory, "readability": body.readability})
    bottlenecks = db.query(BottleneckRecord).filter(BottleneckRecord.session_id == s.id).all()
    return {"selections": {str(b.id): kind for b in bottlenecks}}


@router.get("/{sid}/diff", response_model=OptimizeDiffOut)
def diff(sid: int, variant: str = "balanced", db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own(db, user, sid)
    kind = (variant or "").strip() or "balanced"
    bottlenecks = db.query(BottleneckRecord).filter(BottleneckRecord.session_id == s.id).order_by(BottleneckRecord.id).all()
    new_code = s.code or ""
    for b in bottlenecks:
        v = db.query(OptimizedVariant).filter(
            OptimizedVariant.session_id == s.id,
            OptimizedVariant.bottleneck_id == b.id,
            OptimizedVariant.kind == kind,
        ).first()
        if not v:
            v = db.query(OptimizedVariant).filter(
                OptimizedVariant.session_id == s.id,
                OptimizedVariant.bottleneck_id == b.id,
            ).order_by(OptimizedVariant.id).first()
        if v and b.snippet and b.snippet in new_code:
            new_code = new_code.replace(b.snippet, v.code, 1)
    return OptimizeDiffOut(diff=diff_service.unified(s.code or "", new_code))
