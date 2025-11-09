"""AI service for generating farming plans"""

import json
from google import genai
from dotenv import load_dotenv
from calender.config import PROMPT_EXAMPLES

load_dotenv()


class AIService:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = 'AI-2.5-flash'
    
    def generate_farming_plan(self, user_prompt, language):
        """Generate a farming plan using AI AI"""
        AI_prompt = f"""
        As a farming expert, create a concise, practical plan for the following task. 
        Provide the output in a single, valid JSON object.
        The plan should be in {language} language.
        
        The JSON object must have two keys: 'heading' and 'plan'.
        - 'heading': A short, clear title for the task (less than 5 words)
        - 'plan': A list of steps, where each step has: 'step_number', 'title', and 'description'
        
        Make the plan practical, specific, and easy to follow for farmers.
        Include timing, quantities, and important warnings when relevant.
        
        Example output format:
        {json.dumps(PROMPT_EXAMPLES[language], indent=4, ensure_ascii=False)}
        
        Farmer's Task: {user_prompt}
        """
        
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


