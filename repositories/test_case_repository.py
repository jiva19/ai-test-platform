import json
from db_models import db, TestCaseEntity

def create_test_case(project_id, name, preconditions, steps, expected_result):
    test_case = TestCaseEntity(
        project_id=project_id,
        name=name,
        preconditions=json.dumps(preconditions),
        steps=json.dumps(steps),
        expected_result=expected_result
    )
    db.session.add(test_case)
    db.session.commit()
    return test_case.id

def get_test_cases_for_project(project_id):
    entities = TestCaseEntity.query.filter_by(project_id=project_id).all()
    return [{"id": t.id, "name": t.name} for t in entities]

def get_test_case_by_id(test_case_id):
    t = TestCaseEntity.query.get(test_case_id)
    if t is None:
        return None
    return {
        "id": t.id,
        "name": t.name,
        "preconditions": json.loads(t.preconditions),
        "steps": json.loads(t.steps),
        "expected_result": t.expected_result
    }