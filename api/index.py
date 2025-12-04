#!/usr/bin/env python3
"""
Vercel Serverless Entry Point for FARM-TAK-AI
"""
import sys
import os

# Add the website directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'website'))

# Import the Flask app
from FINAL_FARMER_VOICE_AGENT import app

# Vercel serverless function handler
def handler(request, response):
    """Handle requests via Vercel serverless"""
    return app(request, response)

# For local testing
if __name__ == "__main__":
    app.run(debug=True)
