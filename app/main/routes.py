"""
Main blueprint route handlers.
"""

from flask import render_template, request, current_app, jsonify, Response, url_for
from datetime import datetime

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


# --- SEO: robots.txt and sitemap.xml routes ---


@bp.route("/robots.txt")
def robots_txt():
    """Serve robots.txt for search engine crawlers."""
    # SEO: Allow all user agents, reference sitemap location
    sitemap_url = url_for("main.sitemap_xml", _external=True)
    content = "User-agent: *\n" "Allow: /\n" f"\nSitemap: {sitemap_url}\n"
    return Response(content, mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap_xml():
    """Generate and serve a valid XML sitemap for all public routes."""
    # SEO: Include all publicly accessible pages
    pages = []
    # Static public routes with their change frequency and priority
    routes_config = [
        {"endpoint": "main.index", "changefreq": "weekly", "priority": "1.0"},
        {"endpoint": "main.analysis", "changefreq": "monthly", "priority": "0.8"},
    ]
    lastmod = datetime.now().strftime("%Y-%m-%d")

    for route in routes_config:
        pages.append(
            {
                "loc": url_for(route["endpoint"], _external=True),
                "lastmod": lastmod,
                "changefreq": route["changefreq"],
                "priority": route["priority"],
            }
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += "  <url>\n"
        xml += f"    <loc>{page['loc']}</loc>\n"
        xml += f"    <lastmod>{page['lastmod']}</lastmod>\n"
        xml += f"    <changefreq>{page['changefreq']}</changefreq>\n"
        xml += f"    <priority>{page['priority']}</priority>\n"
        xml += "  </url>\n"
    xml += "</urlset>\n"

    return Response(xml, mimetype="application/xml")


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
                    selected_groups = request.form.getlist("selected_groups")
                    processor = CSVProcessor()
                    results = processor.process(file, selected_groups)

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


@bp.route("/api/detect-columns", methods=["POST"])
def detect_columns():
    """
    AJAX endpoint to detect groupable columns in an uploaded CSV file.

    Returns JSON list of column names suitable for grouping.
    """
    if "csv_file" not in request.files:
        return jsonify({"error": "Datoteka nije učitana"}), 400

    file = request.files["csv_file"]
    if file.filename == "" or not file.filename.endswith(".csv"):
        return jsonify({"error": "Molimo učitajte CSV datoteku"}), 400

    try:
        processor = CSVProcessor()
        columns = processor.detect_groupable_columns(file)
        return jsonify({"columns": columns})
    except UnsupportedEncodingError as e:
        return jsonify({"error": str(e.message)}), 400
    except AppException as e:
        return jsonify({"error": str(e.message)}), 400
    except Exception as e:
        current_app.logger.error(f"Error detecting columns: {str(e)}")
        return (
            jsonify(
                {"error": "Došlo je do neočekivane greške prilikom analize datoteke"}
            ),
            500,
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
        model = current_app.config.get("GEMINI_MODEL", "")
        fallback_models = current_app.config.get("GEMINI_FALLBACK_MODELS", [])
        ai_service = GeminiAIService(api_key, model=model, fallback_models=fallback_models)
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
