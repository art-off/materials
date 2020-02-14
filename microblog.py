from app import app, db
from app.models import User, Material, Email, Test


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Material': Material, 'Email': Email, 'Test': Test}
