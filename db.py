import click

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from .config import DATABASE
from .models import User


engine = create_engine(f"sqlite:///{DATABASE}")
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

DbTableBase = declarative_base()
DbTableBase.query = db_session.query_property()


@click.command('init-db')
def init_db():
    """Clear the existing data and create new tables."""
    DbTableBase.metadata.create_all(bind=engine)
    
    click.echo('Initialized the database.')


def close_db():
    """Teardown the database when the app stops."""
    db_session.remove()


if __name__ == '__main__':
    pass
