from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.bottleneck_record import BottleneckRecord
from app.models.optimization_session import OptimizationSession
from app.models.optimized_variant import OptimizedVariant
from app.models.user import User


def test_session_bottleneck_variants_link():
    for table in (OptimizedVariant.__table__, BottleneckRecord.__table__,
                  OptimizationSession.__table__, User.__table__):
        table.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    u = User(email="t8@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)
    s = OptimizationSession(
        user_id=u.id,
        language="python",
        code="for i in range(10):\n    print(i)",
        runtime={"traffic": "1000 concurrent", "input_size": "1M rows"},
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    assert s.language == "python"
    b = BottleneckRecord(
        session_id=s.id,
        function="process",
        root_cause="nested loops",
        predicted_ms=550.0,
        priority="critical",
        snippet="for i in x:\n for j in y: ...",
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    variants = [
        OptimizedVariant(
            session_id=s.id,
            bottleneck_id=b.id,
            kind="speed",
            code="# speed variant",
            complexity="O(n)",
            readability=4,
            explanation="list comprehension",
        ),
        OptimizedVariant(
            session_id=s.id,
            bottleneck_id=b.id,
            kind="memory",
            code="# memory variant",
            complexity="O(n)",
            readability=6,
            explanation="generator",
        ),
        OptimizedVariant(
            session_id=s.id,
            bottleneck_id=b.id,
            kind="balanced",
            code="# balanced variant",
            complexity="O(n)",
            readability=8,
            explanation="commented listcomp",
        ),
    ]
    db.add_all(variants)
    db.commit()
    assert db.query(BottleneckRecord).filter_by(session_id=s.id).count() == 1
    assert db.query(OptimizedVariant).filter_by(session_id=s.id).count() == 3
    assert db.query(OptimizedVariant).filter_by(bottleneck_id=b.id).count() == 3
    assert b.session_id == s.id
    for v in db.query(OptimizedVariant).filter_by(bottleneck_id=b.id).all():
        assert v.session_id == s.id
    db.close()
