import sys
import os

# Add website directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'website'))

# Import and export the Flask app directly
from FINAL_FARMER_VOICE_AGENT import app
