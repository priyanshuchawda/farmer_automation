# ai/ai_matcher.py

import os
import sqlite3
import pandas as pd
from google import genai

# --- Initialize AI AI Client ---
client = None
try:
    # The API key is automatically picked up from the GEMINI_API_KEY environment variable.
    client = genai.Client()
except Exception as e:
    print(f"Warning: Failed to initialize AI AI client: {e}. AI suggestions will be unavailable.")

DB_NAME = "farmermarket.db"


def fetch_recent_data():
    """
    Fetch recent data from the SQLite database.
    Returns a dictionary containing 'tools' and 'crops' DataFrames.
    """
    conn = sqlite3.connect(DB_NAME)
    try:
        tools_df = pd.read_sql_query("SELECT * FROM tools ORDER BY rowid DESC LIMIT 10", conn)
        crops_df = pd.read_sql_query("SELECT * FROM crops ORDER BY rowid DESC LIMIT 10", conn)
    except Exception as e:
        print(f"Error fetching data from DB: {e}")
        tools_df = pd.DataFrame()
        crops_df = pd.DataFrame()
    finally:
        conn.close()

    return {
        "tools": tools_df,
        "crops": crops_df
    }


def get_recommendations(context: dict):
    """
    Generate AI-powered marketplace recommendations based on context and recent DB data.
    Returns a string with suggestions or a fixed error message if AI is unavailable.
    
    :param context: Dictionary containing user context or preferences.
    """
    if not client:
        return "(AI suggestion unavailable: AI AI client not initialized.)"

    # Fetch recent database data
    recent_data = fetch_recent_data()
    
    # System instruction - defines role and behavior
    system_instruction = """You are an expert marketplace advisor for Indian farmers.
Your role is to analyze marketplace activity and provide practical, actionable recommendations.

Key principles:
- Suggest complementary items that create value
- Consider seasonal farming patterns
- Focus on budget-friendly, practical solutions for small farmers
- Provide concise recommendations (2-3 points maximum)
- Use clear, simple language"""

    # Task prompt - optimized with clear structure and examples
    task_prompt = f"""Analyze this farmer's marketplace activity and provide strategic recommendations.

CONTEXT:
Farmer: {context.get('farmer', 'A farmer')} from {context.get('location', 'their area')}
Action: Just listed {context.get('item')} for {'rent' if context.get('type') == 'tool' else 'sale'}
Listing Type: {context.get('type', 'unknown')}

MARKETPLACE SNAPSHOT:
Active Tool Listings: {len(recent_data['tools'])}
{recent_data['tools'][['Tool', 'Location']].to_dict(orient='records') if not recent_data['tools'].empty else 'No tools available'}

Active Crop Listings: {len(recent_data['crops'])}
{recent_data['crops'][['Crop', 'Location']].to_dict(orient='records') if not recent_data['crops'].empty else 'No crops available'}

TASK:
Generate exactly 3 actionable recommendations considering:
1. Complementary items or services they could add
2. Regional market opportunities
3. Timing and seasonal advantages

FEW-SHOT EXAMPLES:

Input: Tractor listed for rent
Output:
- List plow and seeder together - tractor renters need complete tillage equipment (bundle pricing increases income 30%)
- Wheat planting season approaching - advertise your equipment for land preparation work
- Partner with 2-3 nearby farmers for equipment co-sharing to maximize utilization rate

Input: Wheat listed for sale
Output:
- Harvester available for rent nearby in {context.get('location', 'your area')} - book now to speed up next harvest cycle
- Rotate with pulses (chickpea/lentils) next season - restores soil nitrogen naturally and diversifies revenue
- Current MSP is ₹2275/quintal - verify mandi rates before accepting offers below this support price

Output exactly 3 recommendations starting with "- "
Focus on specific, measurable actions with clear benefits.

RECOMMENDATIONS:
-"""

    try:
        from google.genai import types
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=task_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,  # Slightly creative but consistent
                max_output_tokens=300  # Keep it concise
            )
        )
        return response.text
    except Exception as e:
        return f"(AI suggestion unavailable due to an error: {e})"


