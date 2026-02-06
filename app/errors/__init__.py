"""
Errors blueprint initialization and error handlers.
"""
from flask import Blueprint, render_template, request, jsonify
from werkzeug.exceptions import HTTPException

bp = Blueprint('errors', __name__)


def wants_json_response():
    """Check if the client prefers JSON response over HTML."""
    return request.accept_mimetypes['application/json'] >= \
           request.accept_mimetypes['text/html']


@bp.app_errorhandler(400)
def bad_request_error(error):
    """Handle 400 Bad Request errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    return render_template('errors/400.html', error=error), 400


@bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    return render_template('errors/403.html', error=error), 403


@bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    return render_template('errors/404.html', error=error), 404


@bp.app_errorhandler(413)
def request_entity_too_large(error):
    """Handle 413 Request Entity Too Large errors (file upload too big)."""
    if wants_json_response():
        return jsonify({
            'error': 'File Too Large',
            'message': 'The uploaded file exceeds the maximum allowed size'
        }), 413
    return render_template('errors/413.html', error=error), 413


@bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    if wants_json_response():
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    return render_template('errors/500.html', error=error), 500


@bp.app_errorhandler(Exception)
def handle_exception(error):
    """
    Global exception handler - catches all unhandled exceptions.
    Similar to ExceptionMiddleware in .NET applications.
    """
    # Pass through HTTP errors
    if isinstance(error, HTTPException):
        return error
    
    # Log the error (in production, you'd want proper logging)
    import traceback
    traceback.print_exc()
    
    if wants_json_response():
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    return render_template('errors/500.html', error=error), 500
