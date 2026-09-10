from db_models import db, Project

def create_project(name):
    project = Project(name=name)
    db.session.add(project)
    db.session.commit()
    return project.id

def get_all_projects():
    return [{"id": p.id, "name": p.name} for p in Project.query.all()]