import datetime
import os
import threading
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from models import TestCase
from orchestrator import run_test
from repositories.results_repository import start_run, get_run, get_all_runs
from db_models import db, Project, TestCaseEntity, TestRunEntity
from repositories.project_repository import create_project, get_all_projects
from repositories.test_case_repository import create_test_case, get_test_cases_for_project, get_test_case_by_id
from repositories.results_repository import get_runs_for_test_case



load_dotenv()

app = Flask(__name__)

connection_url = URL.create(
    "mssql+pymssql",
    username="sa",
    password=os.getenv("DB_PASSWORD"),
    host="localhost",
    port=1433,
    database="HrManagement"
)
app.config['SQLALCHEMY_DATABASE_URI'] = connection_url

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")



def run_test_in_context(test_case, db_id, run_id):
    with app.app_context():
        run_test(test_case, db_id, run_id)

@app.route("/run-test", methods=["POST"])
def run_test_endpoint():
    data = request.get_json()

    test_case_id = data["test_case_id"]

    saved = get_test_case_by_id(test_case_id)
    if saved is None:
        return jsonify({"error": "test case not found"}), 404

    test_case = TestCase(
        name=saved["name"],
        preconditions=saved["preconditions"],
        steps=saved["steps"],
        expected_result=saved["expected_result"]
    )


    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    db_id = start_run(test_case_id, run_id)

    thread = threading.Thread(target=run_test_in_context, args=(test_case, db_id, run_id))
    thread.start()

    return jsonify({"id": db_id, "status": "started"}), 202



@app.route("/projects", methods=["POST"])
def create_project_endpoint():
    data = request.get_json()
    project_id = create_project(data["name"])
    return jsonify({"id": project_id}), 201

@app.route("/projects", methods=["GET"])
def list_projects_endpoint():
    return jsonify(get_all_projects())

@app.route("/projects/<int:project_id>/test-cases", methods=["POST"])
def create_test_case_endpoint(project_id):
    data = request.get_json()
    test_case_id = create_test_case(
        project_id,
        data["name"],
        data["preconditions"],
        data["steps"],
        data["expected_result"]
    )
    return jsonify({"id": test_case_id}), 201

@app.route("/projects/<int:project_id>/test-cases", methods=["GET"])
def list_test_cases_endpoint(project_id):
    return jsonify(get_test_cases_for_project(project_id))

@app.route("/test-cases/<int:test_case_id>", methods=["GET"])
def get_test_case_endpoint(test_case_id):
    tc = get_test_case_by_id(test_case_id)
    if tc is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(tc)

@app.route("/test-cases/<int:test_case_id>/runs", methods=["GET"])
def get_test_case_runs_endpoint(test_case_id):
    return jsonify(get_runs_for_test_case(test_case_id))


@app.route("/results/<int:db_id>", methods=["GET"])
def get_result(db_id):
    run = get_run(db_id)
    if run is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(run)

@app.route("/results", methods=["GET"])
def list_results():
    return jsonify(get_all_runs())

if __name__ == "__main__":
    app.run(debug=True, port=5001)