from engine.engine import UnifiedPredictionEngine

def test_engine_loads():
    engine = UnifiedPredictionEngine()
    assert engine is not None
