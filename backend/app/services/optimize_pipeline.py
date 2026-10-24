"""Submit orchestration: analyse -> hotspots -> bottlenecks -> variants."""

from app.models.optimization_session import OptimizationSession
from app.models.bottleneck_record import BottleneckRecord
from app.models.optimized_variant import OptimizedVariant
from app.services import ast_analyser, profiler
from app.services import bottleneck_predictor as predictor
from app.services import optimisation_generator as generator


def submit(db, user_id: int, code: str, language: str, runtime: dict) -> dict:
    analysis = ast_analyser.analyse(code or "", language or "python")
    hotspots = profiler.profile(analysis)
    scale = predictor.parse_scale(runtime or {})
    bottlenecks = predictor.predict(hotspots, scale)
    session = OptimizationSession(user_id=user_id, language=language or "python",
                                  code=code or "", runtime=dict(runtime or {}))
    db.add(session)
    db.commit()
    db.refresh(session)
    out_bn = []
    for bn in bottlenecks:
        # bottleneck predictor returns snippet-less rows? keep snippet from hotspot
        row = BottleneckRecord(session_id=session.id, function=bn["function"],
                               root_cause=bn["root_cause"],
                               predicted_ms=bn["predicted_ms"],
                               priority=bn["priority"], snippet=bn.get("snippet", ""))
        db.add(row)
        db.commit()
        db.refresh(row)
        sig = (next((h["signals"][0] for h in hotspots
                     if h["function"] == bn["function"] and h["signals"]), ""))
        kinds = generator.variants(bn.get("snippet", ""), sig, language or "python")
        for kind, v in kinds.items():
            db.add(OptimizedVariant(session_id=session.id, bottleneck_id=row.id,
                                    kind=kind, code=v["code"],
                                    complexity=v["time_complexity"],
                                    readability=v["readability"],
                                    explanation=v["explanation"]))
        db.commit()
        out_bn.append({"id": row.id, "function": row.function,
                       "root_cause": row.root_cause,
                       "predicted_ms": row.predicted_ms,
                       "priority": row.priority, "snippet": row.snippet})
    return {"session_id": session.id, "hotspots": hotspots, "bottlenecks": out_bn}
