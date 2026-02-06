# CSV Statistics Calculator

A Flask application for calculating statistics on Likert scale survey data from Google Forms.

## Project Structure

```
DiplomskiCSVStatistika/
├── app/                          # Main application package
│   ├── __init__.py               # Application factory
│   ├── config.py                 # Configuration classes
│   ├── main/                     # Main blueprint
│   │   ├── __init__.py           # Blueprint initialization
│   │   └── routes.py             # Route handlers
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── statistics.py         # Statistical calculations
│   │   └── csv_processor.py      # CSV file processing
│   └── templates/                # Jinja2 templates
│       └── index.html
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```

4. Run the application:
   ```bash
   python run.py
   ```

## Production Deployment

For production, use Gunicorn (Linux/Mac):
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

Make sure to set `FLASK_ENV=production` and generate a secure `SECRET_KEY`.

## Architecture

- **Application Factory Pattern**: `create_app()` in `app/__init__.py` allows for flexible configuration
- **Blueprints**: Routes are organized into blueprints for modularity
- **Services Layer**: Business logic is separated from route handlers
- **Configuration Classes**: Environment-specific settings (dev, prod, test)
