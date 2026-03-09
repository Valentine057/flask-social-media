import click

from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask import current_app


class DbTableBase(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = DbTableBase)

@click.command('init-db')
def init_db():
    """Clear the existing data and create new tables."""
    from .models import views, MyCustomCreateView
    
    with current_app.app_context():
        db.create_all()
    
    with db.engine.connect() as connection:
        for view in views:
            connection.execute(MyCustomCreateView(view))
    
    click.echo('Initialized the database.')


def close_db(exception=None):
    """Teardown the database when the app stops."""
    db.session.remove()


if __name__ == '__main__':
    pass
