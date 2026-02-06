"""
Application entry point.
"""
import os
from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

# Determine configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')

if env == 'production':
    config_class = ProductionConfig
else:
    config_class = DevelopmentConfig

app = create_app(config_class)

if __name__ == '__main__':
    app.run()
