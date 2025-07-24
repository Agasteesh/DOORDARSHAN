import os
from app import create_app, db
from app.models import User, Content, Genre
from flask_migrate import Migrate
from config import config_map

config_name = os.environ.get('FLASK_CONFIG', 'development') 

if config_name not in config_map:
    print(f"Warning: Configuration '{config_name}' not found in config_map. Using 'development' configuration.")
    config_name = 'development'

app = create_app(config_map[config_name])

# migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Content=Content, Genre=Genre)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
