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
    UnsupportedEncodingError,
)


@bp.route("/")
def index():
    """Homepage — explains what the app does."""
    return render_template("home.html")


@bp.route("/analysis", methods=["GET", "POST"])
def analysis():
    """
    Analysis page route handler.

    GET: Display the upload form.
    POST: Process uploaded CSV file and display statistics.
    """
    results = None
    error = None

    if request.method == "POST":
        if "csv_file" not in request.files:
            error = "Datoteka nije učitana"
        else:
            file = request.files["csv_file"]
            if file.filename == "":
                error = "Datoteka nije odabrana"
            elif not file.filename.endswith(".csv"):
                error = "Molimo učitajte CSV datoteku"
            else:
                try:
                    processor = CSVProcessor(
                        grouping_columns=current_app.config["GROUPING_COLUMNS"],
                        grouping_labels=current_app.config["GROUPING_LABELS"],
                    )
                    results = processor.process(file)

                    if not results["overall"]:
                        error = "Nisu pronađena pitanja s Likertovom skalom (1-5) u CSV datoteci"
                        results = None
                except UnsupportedEncodingError as e:
                    error = str(e.message)
                except AppException as e:
                    error = str(e.message)
                except Exception as e:
                    current_app.logger.error(
                        f"Unexpected error processing file: {str(e)}"
                    )
                    error = "Došlo je do neočekivane greške prilikom obrade datoteke"

    return render_template("analysis.html", results=results, error=error)
