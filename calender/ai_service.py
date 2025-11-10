"""AI service for generating farming plans"""

import json
from google import genai
from dotenv import load_dotenv
from calender.config import PROMPT_EXAMPLES

load_dotenv()


class AIService:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = 'gemini-2.5-flash'
    
    def generate_farming_plan(self, user_prompt, language):
        """Generate a farming plan using Gemini AI"""
        AI_prompt = f"""Generate a step-by-step farming task plan in {language} language.

FARMER REQUEST:
{user_prompt}

OUTPUT REQUIREMENTS:
Return a single valid JSON object with this exact structure:

{{
  "heading": "Short task title (max 5 words)",
  "plan": [
    {{
      "step_number": 1,
      "title": "Step title",
      "description": "Detailed instructions with timing, quantities, tools needed"
    }}
  ]
}}

PLAN QUALITY STANDARDS:
1. Practical: Include specific timings (e.g., "7 AM", "after 3 days"), quantities (e.g., "2 kg seeds per acre"), tools
2. Safety: Add warnings for pesticides, heavy equipment, weather precautions
3. Sequential: Each step builds on previous ones logically
4. Farmer-friendly: Use simple {language} language, avoid technical jargon
5. Regional: Consider Indian agricultural practices and seasons
6. Complete: Cover preparation, execution, and follow-up

EXAMPLE OUTPUT IN {language}:
{json.dumps(PROMPT_EXAMPLES[language], indent=2, ensure_ascii=False)}

Generate plan for: {user_prompt}

Output only the JSON object, no additional text."""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name, 
                contents=AI_prompt
            )
            # Clean the response to ensure it is a valid JSON string
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            plan_data = json.loads(cleaned_response)
            
            if isinstance(plan_data, dict) and 'heading' in plan_data and 'plan' in plan_data:
                if isinstance(plan_data['plan'], list):
                    return plan_data, None
                else:
                    return None, "Invalid plan format received."
            else:
                return None, "The AI response was not in the expected format."
                
        except json.JSONDecodeError:
            return None, "Could not parse the AI response. Please try again."
        except Exception as e:
            return None, f"An error occurred: {str(e)}"


