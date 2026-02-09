"""
Main blueprint route handlers.
"""

from flask import render_template, request, current_app, jsonify

from app.main import bp
from app.services.csv_processor import CSVProcessor
from app.services.gemini_ai import GeminiAIService
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

    return render_template(
        "analysis.html",
        results=results,
        error=error,
        ai_enabled=current_app.config.get("GEMINI_AI_ENABLED", False),
    )


@bp.route("/api/ai-analysis", methods=["POST"])
def ai_analysis():
    """
    AJAX endpoint for AI interpretation of statistical results.

    Reads previously stored results from the session and sends them
    to the Gemini AI service.
    """
    ai_enabled = current_app.config.get("GEMINI_AI_ENABLED", False)
    api_key = current_app.config.get("GEMINI_API_KEY", "")

    if not ai_enabled or not api_key:
        return jsonify({"error": "AI analiza nije omogućena."}), 400

    data = request.get_json()
    if not data or not data.get("overall"):
        return (
            jsonify(
                {
                    "error": "Nema podataka za analizu. Molimo prvo učitajte CSV datoteku."
                }
            ),
            400,
        )

    try:
        ai_service = GeminiAIService(api_key)
        interpretation = ai_service.interpret_results(
            overall_stats=data["overall"],
            grouped_stats=data.get("grouped"),
            groupings_info=data.get("groupings"),
        )
        return jsonify({"interpretation": interpretation})
    except Exception as e:
        current_app.logger.error(f"Gemini AI error: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Došlo je do pogreške s AI analizom. Molimo pokušajte kasnije."
                }
            ),
            500,
        )
