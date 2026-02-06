"""
Main blueprint route handlers.
"""
from flask import render_template, request, current_app

from app.main import bp
from app.services.csv_processor import CSVProcessor
from app.errors.exceptions import (
    AppException,
    ValidationError,
    NoLikertDataError,
    UnsupportedEncodingError
)


@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Main page route handler.
    
    GET: Display the upload form.
    POST: Process uploaded CSV file and display statistics.
    """
    results = None
    error = None
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            error = 'No file uploaded'
        else:
            file = request.files['csv_file']
            if file.filename == '':
                error = 'No file selected'
            elif not file.filename.endswith('.csv'):
                error = 'Please upload a CSV file'
            else:
                try:
                    processor = CSVProcessor(
                        grouping_columns=current_app.config['GROUPING_COLUMNS'],
                        grouping_labels=current_app.config['GROUPING_LABELS']
                    )
                    results = processor.process(file)
                    
                    if not results['overall']:
                        error = 'No questions with 1-5 scale answers found in the CSV file'
                        results = None
                except UnsupportedEncodingError as e:
                    error = str(e.message)
                except AppException as e:
                    error = str(e.message)
                except Exception as e:
                    current_app.logger.error(f'Unexpected error processing file: {str(e)}')
                    error = 'An unexpected error occurred while processing the file'
    
    return render_template('index.html', results=results, error=error)
