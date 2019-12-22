from app import create_app, db_relational

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db_relational': db_relational,
    }
