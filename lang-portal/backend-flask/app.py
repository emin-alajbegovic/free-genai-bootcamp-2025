from flask import Flask, g
from flask_cors import CORS
import sqlite3
import os

from lib.db import Db

import routes.words
import routes.groups
import routes.study_sessions
import routes.dashboard
import routes.study_activities

def get_allowed_origins(app):
    try:
        cursor = app.db.cursor()
        cursor.execute('SELECT url FROM study_activities')
        urls = cursor.fetchall()
        # Convert URLs to origins (e.g., https://example.com/app -> https://example.com)
        origins = set()
        for url in urls:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url['url'])
                origin = f"{parsed.scheme}://{parsed.netloc}"
                origins.add(origin)
            except:
                continue
        return list(origins) if origins else ["*"]
    except:
        return ["*"]  # Fallback to allow all origins if there's an error

def get_db(app):
    if 'db' not in g:
        if app.config['TESTING']:
            g.db = sqlite3.connect(':memory:', check_same_thread=False)
            # Initialize test database schema here
            with app.open_resource('schema.sql', mode='r') as f:
                g.db.executescript(f.read())
        else:
            g.db = sqlite3.connect('database.db', check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['DATABASE'] = ':memory:'
    else:
        app.config['TESTING'] = False
        app.config['DATABASE'] = 'database.db'
    
    # Database setup
    with app.app_context():
        if app.config['TESTING']:
            db = get_db(app)
            # Initialize test database schema
            with app.open_resource('schema.sql', mode='r') as f:
                db.executescript(f.read())
    
    # Initialize database first since we need it for CORS configuration
    app.db = Db(database=app.config['DATABASE'])
    
    # Get allowed origins from study_activities table
    allowed_origins = get_allowed_origins(app)
    
    # In development, add localhost to allowed origins
    if app.debug:
        allowed_origins.extend(["http://localhost:8080", "http://127.0.0.1:8080"])
    
    # Configure CORS with combined origins
    CORS(app, resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Close database connection
    @app.teardown_appcontext
    def close_db(exception):
        app.db.close()

    # load routes -----------
    routes.words.load(app)
    routes.groups.load(app)
    routes.study_sessions.load(app)
    routes.dashboard.load(app)
    routes.study_activities.load(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)