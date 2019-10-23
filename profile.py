# profile.py

from app import create_app, db, limiter

app = create_app()
#
@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, limiter=limiter)
