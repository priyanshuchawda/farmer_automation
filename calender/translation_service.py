"""Translation service using deep-translator"""

from deep_translator import GoogleTranslator


class TranslationService:
    """Handle text translation for farming plans"""
    
    def __init__(self):
        self.language_codes = {
            'en': 'en',
            'hi': 'hi',
            'mr': 'mr'
        }
    
    def translate_text(self, text, target_lang, source_lang='auto'):
        """Translate text to target language"""
        if not text:
            return text
            
        try:
            translator = GoogleTranslator(source=source_lang, target=self.language_codes[target_lang])
            translated = translator.translate(text)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def translate_plan(self, plan_data, target_lang, source_lang='auto'):
        """Translate entire plan data structure"""
        try:
            # Translate heading
            translated_plan = {
                'heading': self.translate_text(plan_data['heading'], target_lang, source_lang),
                'plan': []
            }
            
            # Translate each step
            for step in plan_data['plan']:
                translated_step = {
                    'step_number': step['step_number'],
                    'title': self.translate_text(step['title'], target_lang, source_lang),
                    'description': self.translate_text(step['description'], target_lang, source_lang)
                }
                translated_plan['plan'].append(translated_step)
            
            return translated_plan
        except Exception as e:
            print(f"Plan translation error: {e}")
            return plan_data  # Return original if translation fails
    
    def translate_event(self, event, target_lang, source_lang='auto'):
        """Translate event data"""
        try:
            # Create a deep copy of the event
            import copy
            translated_event = copy.deepcopy(event)
            
            # Translate heading
            if 'extendedProps' in translated_event:
                translated_event['extendedProps']['heading'] = self.translate_text(
                    event['extendedProps']['heading'], 
                    target_lang,
                    source_lang
                )
                
                # Translate title
                translated_event['title'] = f"{translated_event['extendedProps']['heading']} 📝"
                
                # Translate plan steps
                translated_steps = []
                for step in event['extendedProps']['plan']:
                    translated_step = {
                        'step_number': step['step_number'],
                        'title': self.translate_text(step['title'], target_lang, source_lang),
                        'description': self.translate_text(step['description'], target_lang, source_lang)
                    }
                    translated_steps.append(translated_step)
                
                translated_event['extendedProps']['plan'] = translated_steps
            
            return translated_event
        except Exception as e:
            print(f"Event translation error: {e}")
            return event
