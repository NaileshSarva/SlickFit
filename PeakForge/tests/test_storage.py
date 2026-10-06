import tempfile
from pathlib import Path

from src.peakforge.models import AthleteParams, PerformanceTest, TrainingSession
from src.peakforge.storage import PeakForgeStore


def test_store_roundtrip_sessions():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        store = PeakForgeStore(db_path)

        store.add_session(TrainingSession(date="2026-01-01", load=60.0))
        store.add_session(TrainingSession(date="2026-01-02", load=45.0))

        sessions = store.list_sessions()
        assert len(sessions) == 2
        assert sessions[0].date == "2026-01-01"
        assert sessions[1].load == 45.0
        store.close()


def test_store_roundtrip_performance_tests():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        store = PeakForgeStore(db_path)

        store.add_performance_test(PerformanceTest(date="2026-01-05", score=12.4))
        tests = store.list_performance_tests()
        assert len(tests) == 1
        assert tests[0].score == 12.4
        store.close()


def test_store_latest_params():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        store = PeakForgeStore(db_path)

        assert store.latest_params() is None

        store.save_params(AthleteParams(k1=1.0, k2=1.5, tau1=42, tau2=7, p0=0.0, residual_error=0.1))
        store.save_params(AthleteParams(k1=1.2, k2=1.6, tau1=40, tau2=8, p0=0.5, residual_error=0.05))

        latest = store.latest_params()
        assert latest.k1 == 1.2
        assert latest.residual_error == 0.05
        store.close()
