"""
Vercel Serverless Entry Point for FARM-TAK-AI
Flask application deployed as Vercel serverless function
"""
import sys
import os

# Add parent directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
website_dir = os.path.join(parent_dir, 'website')
sys.path.insert(0, parent_dir)
sys.path.insert(0, website_dir)

# Import the Flask app from the website directory
try:
    from website.FINAL_FARMER_VOICE_AGENT import app
except ImportError:
    # Fallback import if running from different context
    import FINAL_FARMER_VOICE_AGENT
    app = FINAL_FARMER_VOICE_AGENT.app

# Export the app for Vercel
# Vercel automatically wraps Flask apps with WSGI
# No custom handler needed - just export 'app'
