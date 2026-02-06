"""
Application configuration module.
"""
import os


class Config:
    """Base configuration class."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Grouping columns configuration for the survey
    GROUPING_COLUMNS = {
        'age': 'Dobna skupina kojoj pripadate',
        'experience': 'Radno iskustvo u odgojno-obrazovnom sustavu',
        'area': 'Područje djelovanja tijekom posljednjih 10 godina rada'
    }
    
    GROUPING_LABELS = {
        'age': 'Dobna skupina',
        'experience': 'Radno iskustvo',
        'area': 'Područje djelovanja'
    }


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    # In production, ensure SECRET_KEY is set via environment variable
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        return key


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
