import os
import streamlit as st
from dotenv import load_dotenv

# Smart environment loading: Works both locally and on Streamlit Cloud
if os.getenv("STREAMLIT_RUNTIME") is None:
    load_dotenv()  # Load .env only if running locally

def get_api_key():
    """Get the OpenWeather API key from environment variables or Streamlit secrets."""
    # Try Streamlit secrets first (cloud), then environment variables (local)
    try:
        return st.secrets.get("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API_KEY")
    except:
        return os.getenv("OPENWEATHER_API_KEY")

def get_gemini_api_key():
    """Get the Gemini API key from environment variables or Streamlit secrets."""
    # Try Streamlit secrets first (cloud), then environment variables (local)
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except:
        return os.getenv("GEMINI_API_KEY")

PUNE_COORDINATES = {"lat": 18.5204, "lon": 73.8567}


