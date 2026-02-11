"""
Application configuration module.
"""

import os


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_AI_ENABLED = os.environ.get("GEMINI_AI_ENABLED", "true").lower() in (
        "true",
        "1",
        "yes",
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False

    # In production, ensure SECRET_KEY is set via environment variable
    @property
    def SECRET_KEY(self):
        key = os.environ.get("SECRET_KEY")
        if not key:
            raise ValueError(
                "SECRET_KEY environment variable must be set in production"
            )
        return key


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
