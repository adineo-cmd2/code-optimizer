from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.optimization_session import OptimizationSession
from app.models.bottleneck_record import BottleneckRecord
from app.models.user import User

router = APIRouter()


@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    out = []
    sessions = db.query(OptimizationSession).filter(
        OptimizationSession.user_id == user.id
    ).order_by(OptimizationSession.id).all()
    for s in sessions:
        count = db.query(BottleneckRecord).filter(BottleneckRecord.session_id == s.id).count()
        created = s.created_at.isoformat() if getattr(s, "created_at", None) else None
        out.append({"id": s.id, "language": s.language, "created": created, "bottlenecks": count})
    return out
