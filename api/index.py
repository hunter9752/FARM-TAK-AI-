import sys
import os

# Add website directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
website_dir = os.path.join(parent_dir, 'website')
sys.path.insert(0, website_dir)
sys.path.insert(0, parent_dir)

# Import the complete Flask app from website/app.py
from app import app

# Export the app for Vercel
# Vercel will automatically wrap this with WSGI
