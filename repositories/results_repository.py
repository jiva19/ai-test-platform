import datetime
from db_models import db, TestRunEntity

def start_run(test_case_id, run_id):
    run = TestRunEntity(
        test_case_id=test_case_id,
        run_id=run_id,
        result="RUNNING",
        reason="",
        screenshot_dir="",
        timestamp=datetime.datetime.now()
    )
    db.session.add(run)
    db.session.commit()
    return run.id

def complete_run(db_id, test_result, reason, screenshot_dir):
    run = TestRunEntity.query.get(db_id)
    run.result = test_result
    run.reason = reason
    run.screenshot_dir = screenshot_dir
    db.session.commit()

def get_run(db_id):
    run = TestRunEntity.query.get(db_id)
    if run is None:
        return None
    return {
        "id": run.id,
        "test_case_id": run.test_case_id,
        "run_id": run.run_id,
        "result": run.result,
        "reason": run.reason,
        "screenshot_dir": run.screenshot_dir,
        "timestamp": run.timestamp.isoformat()
    }

def get_runs_for_test_case(test_case_id):
    runs = TestRunEntity.query.filter_by(test_case_id=test_case_id).order_by(TestRunEntity.timestamp.desc()).all()
    return [
        {
            "id": r.id,
            "run_id": r.run_id,
            "result": r.result,
            "reason": r.reason,
            "screenshot_dir": r.screenshot_dir,
            "timestamp": r.timestamp.isoformat()
        }
        for r in runs
    ]

def get_all_runs():
    runs = TestRunEntity.query.order_by(TestRunEntity.timestamp.desc()).all()
    return [
        {
            "id": r.id,
            "test_case_id": r.test_case_id,
            "run_id": r.run_id,
            "result": r.result,
            "reason": r.reason,
            "screenshot_dir": r.screenshot_dir,
            "timestamp": r.timestamp.isoformat()
        }
        for r in runs
    ]