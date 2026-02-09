"""
Application factory for LSparrow - Statistical Analysis Application.
"""

from flask import Flask, jsonify, render_template, request

from app.config import Config


def create_app(config_class=Config):
    """
    Application factory function.

    Args:
        config_class: Configuration class to use for the application.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    # Register custom exception handler
    from app.errors.exceptions import AppException

    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """Handle custom application exceptions."""
        if (
            request.accept_mimetypes["application/json"]
            >= request.accept_mimetypes["text/html"]
        ):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response
        return render_template("errors/500.html", error=error), error.status_code

    return app
