"""
Vercel serverless entry point for GombaTar Backend.
Exports Flask app for both Vercel (WSGI) and local gunicorn execution.
"""

from app.main import create_app

app = create_app()
