import sqlite3
import click
from flask import g, current_app


def get_db():
    """Create the database and then return it."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
def init_db():
    """Clear the existing data and create new tables."""
    db = get_db()

    with current_app.open_resource('schema.sql') as file:
        db.executescript(file.read().decode('utf8'))
    
    click.echo('Initialized the database.')


def init_app(app):
    app.cli.add_command(init_db)
    app.teardown_appcontext(close_db)


if __name__ == '__main__':
    pass


