from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'Projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    test_cases = db.relationship('TestCaseEntity', backref='project', lazy=True)

class TestCaseEntity(db.Model):
    __tablename__ = 'TestCases'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('Projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    preconditions = db.Column(db.Text)
    steps = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    runs = db.relationship('TestRunEntity', backref='test_case', lazy=True)

class TestRunEntity(db.Model):
    __tablename__ = 'TestRuns'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=False)
    run_id = db.Column(db.String(50), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text)
    screenshot_dir = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, nullable=False)
