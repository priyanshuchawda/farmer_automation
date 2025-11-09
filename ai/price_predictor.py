# ai/price_predictor.py
"""
AI-Powered Price Prediction and Analysis System
Uses AI AI to predict crop prices, suggest best selling times, and calculate profits
Enhanced with weather data, online news, and current market prices
"""

import os
import requests
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.cache_manager import CacheManager

load_dotenv()

class PricePredictor:
    """AI-powered crop price prediction and analysis system with smart caching."""
    
    def __init__(self):
        """Initialize AI AI for price predictions."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            # Try to use environment variable
            self.client = genai.Client()
        
        # Use Gemini 2.5 Flash with Google Search capability
        self.model = 'gemini-2.5-flash'
        self.model_with_search = 'gemini-2.5-flash'
        
        # Get weather API key
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Initialize cache manager
        self.cache = CacheManager()
        print("📦 Cache system initialized")
    
    def get_weather_data(self, location):
        """
        Fetch current weather and forecast data from OpenWeather API with caching.
        
        Args:
            location: City name (e.g., "Pune, Maharashtra")
        
        Returns:
            dict: Weather data including current conditions and forecast
        """
        if not self.weather_api_key:
            return None
        
        # Check cache first
        cached_weather = self.cache.get_weather_cache(location)
        if cached_weather:
            print(f"   ✅ Using cached weather data for {location}")
            return cached_weather
        
        print(f"   🌐 Fetching fresh weather data for {location}...")
        
        try:
            # Get coordinates first
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.weather_api_key}"
            geo_response = requests.get(geo_url, timeout=10)
            
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                if geo_data:
                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']
                    
                    # Get current weather
                    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
                    weather_response = requests.get(weather_url, timeout=10)
                    
                    # Get 5-day forecast
                    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
                    forecast_response = requests.get(forecast_url, timeout=10)
                    
                    if weather_response.status_code == 200:
                        current = weather_response.json()
                        forecast = forecast_response.json() if forecast_response.status_code == 200 else None
                        
                        weather_data = {
                            'current': {
                                'temperature': current['main']['temp'],
                                'feels_like': current['main']['feels_like'],
                                'humidity': current['main']['humidity'],
                                'pressure': current['main']['pressure'],
                                'weather': current['weather'][0]['description'],
                                'wind_speed': current['wind']['speed'],
                                'rain': current.get('rain', {}).get('1h', 0)
                            },
                            'forecast': self._parse_forecast(forecast) if forecast else None,
                            'location': location
                        }
                        
                        # Cache the weather data for 6 hours
                        self.cache.set_weather_cache(location, weather_data, hours=6)
                        print(f"   💾 Weather data cached for 6 hours")
                        
                        return weather_data
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return None
    
    def _parse_forecast(self, forecast_data):
        """Parse 5-day forecast into daily summaries."""
        if not forecast_data or 'list' not in forecast_data:
            return None
        
        daily_forecasts = []
        current_date = None
        day_data = []
        
        for item in forecast_data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            
            if current_date is None:
                current_date = date
            
            if date != current_date:
                # Summarize the day
                if day_data:
                    temps = [d['main']['temp'] for d in day_data]
                    humidity = [d['main']['humidity'] for d in day_data]
                    rain_prob = max([d.get('pop', 0) * 100 for d in day_data])
                    
                    daily_forecasts.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'temp_max': max(temps),
                        'temp_min': min(temps),
                        'humidity_avg': sum(humidity) / len(humidity),
                        'rain_probability': rain_prob,
                        'weather': day_data[len(day_data)//2]['weather'][0]['description']
                    })
                
                current_date = date
                day_data = [item]
            else:
                day_data.append(item)
        
        return daily_forecasts[:5]  # Return 5 days
    
    def get_online_news_and_prices(self, crop_name, location):
        """
        Use AI with Google Search grounding to find current news and market prices with caching.
        
        Args:
            crop_name: Name of the crop
            location: Location for context
        
        Returns:
            dict: News and current price information with citations
        """
        # Check cache first
        cached_price = self.cache.get_market_price_cache(crop_name, location)
        if cached_price:
            print(f"   ✅ Using cached market data for {crop_name} in {location}")
            return cached_price
        
        print(f"   🌐 Fetching fresh market data for {crop_name} in {location}...")
        
        try:
            search_prompt = f"""Find the current market information for {crop_name} in {location}, India:

1. What is the current wholesale/mandi price of {crop_name} in rupees per quintal?
2. What recent news or developments affect {crop_name} farming or prices in this region?
3. Are there any supply or demand issues currently affecting {crop_name}?
4. Any government policies, MSP announcements, or schemes for {crop_name}?

Provide specific prices with sources."""

            # Use proper grounding with Google Search
            response = self.client.models.generate_content(
                model=self.model_with_search,
                contents=search_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            # Get the response text
            text = response.text
            
            # Extract grounding metadata for citations
            grounding_metadata = None
            sources = []
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_metadata = candidate.grounding_metadata
                    
                    # Extract source URLs
                    if hasattr(grounding_metadata, 'grounding_chunks'):
                        for chunk in grounding_metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    'url': chunk.web.uri,
                                    'title': chunk.web.title if hasattr(chunk.web, 'title') else 'Source'
                                })
            
            # Parse the response intelligently
            import re
            
            # Try to extract price from the text
            current_price = None
            price_patterns = [
                r'₹\s*(\d+[,\d]*\.?\d*)\s*(?:per\s*)?(?:quintal|qtl)',
                r'(?:price|rate).*?₹\s*(\d+[,\d]*\.?\d*)',
                r'(\d+[,\d]*\.?\d*)\s*(?:rupees|rs|inr).*?(?:per\s*)?(?:quintal|qtl)',
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        price_str = matches[0].replace(',', '')
                        current_price = float(price_str)
                        break
                    except:
                        continue
            
            # Extract only JSON-serializable data from grounding_metadata
            search_queries = []
            if grounding_metadata and hasattr(grounding_metadata, 'web_search_queries'):
                search_queries = grounding_metadata.web_search_queries
            
            result = {
                'current_price': current_price,
                'news_summary': text[:500] if len(text) > 500 else text,  # First 500 chars as summary
                'full_response': text,
                'sources': sources,
                'search_queries': search_queries
            }
            
            # Extract key insights from text
            sentences = text.split('.')
            market_conditions = ''
            policy_updates = ''
            
            for sentence in sentences:
                lower = sentence.lower()
                if any(word in lower for word in ['supply', 'demand', 'shortage', 'surplus', 'harvest']):
                    market_conditions += sentence.strip() + '. '
                if any(word in lower for word in ['government', 'policy', 'msp', 'scheme', 'subsidy']):
                    policy_updates += sentence.strip() + '. '
            
            result['market_conditions'] = market_conditions.strip() if market_conditions else 'No specific information found'
            result['policy_updates'] = policy_updates.strip() if policy_updates else 'No recent policy updates found'
            
            # Cache the market data for 24 hours
            self.cache.set_market_price_cache(crop_name, location, result, hours=24)
            print(f"   💾 Market data cached for 24 hours")
            
            return result
            
        except Exception as e:
            import traceback
            print(f"Error in online search: {str(e)}")
            print(traceback.format_exc())
            return {
                'current_price': None,
                'news_summary': 'Unable to fetch current market data',
                'market_conditions': 'Unknown',
                'policy_updates': 'None available',
                'sources': [],
                'error': str(e)
            }
    
    def predict_future_prices(self, crop_name, current_price, location="India", days_ahead=30):
        """
        Predict future crop prices using AI analysis with weather, news, and market data (with smart caching).
        
        Args:
            crop_name: Name of the crop (e.g., "Wheat", "Rice", "Tomato")
            current_price: Current market price per quintal/kg
            location: Location for context (default: India)
            days_ahead: Number of days to predict ahead (default: 30)
        
        Returns:
            dict: Prediction results with prices and confidence
        """
        
        # Check prediction cache first
        cached_prediction = self.cache.get_prediction_cache(crop_name, location, current_price, tolerance=100.0)
        if cached_prediction:
            print(f"✅ Using cached prediction for {crop_name} in {location} (₹{current_price})")
            return cached_prediction
        
        # Gather comprehensive data
        print(f"📊 Gathering data for {crop_name} in {location}...")
        
        # 1. Get weather data
        print("🌤️  Fetching weather data...")
        weather_data = self.get_weather_data(location)
        
        # 2. Get online news and current prices
        print("🔍 Searching online news and current prices...")
        online_data = self.get_online_news_and_prices(crop_name, location)
        
        # Build comprehensive context
        weather_context = ""
        if weather_data:
            current_w = weather_data['current']
            weather_context = f"""
CURRENT WEATHER IN {location}:
- Temperature: {current_w['temperature']:.1f}°C (Feels like: {current_w['feels_like']:.1f}°C)
- Humidity: {current_w['humidity']}%
- Weather: {current_w['weather']}
- Wind Speed: {current_w['wind_speed']} m/s
- Recent Rain: {current_w['rain']} mm"""
            
            if weather_data['forecast']:
                weather_context += "\n\nWEATHER FORECAST (Next 5 days):"
                for day in weather_data['forecast']:
                    weather_context += f"\n- {day['date']}: {day['temp_min']:.0f}-{day['temp_max']:.0f}°C, {day['weather']}, Rain: {day['rain_probability']:.0f}%"
        else:
            weather_context = "\nWEATHER DATA: Not available"
        
        # Build market intelligence
        sources_info = ""
        if online_data.get('sources'):
            sources_info = "\nVerified Sources:\n"
            for i, source in enumerate(online_data['sources'][:5], 1):
                sources_info += f"  {i}. {source.get('title', 'Source')}: {source.get('url', 'N/A')}\n"
        
        market_intelligence = f"""
ONLINE MARKET INTELLIGENCE (Real-time Google Search):
- Latest Market Price Found: {f"₹{online_data['current_price']:.2f} per quintal" if online_data['current_price'] else "Price information not found online"}
- Recent Market Updates: {online_data.get('news_summary', 'N/A')}
- Market Conditions: {online_data.get('market_conditions', 'N/A')}
- Policy Updates: {online_data.get('policy_updates', 'N/A')}{sources_info}"""
        
        prompt = f"""You are an expert agricultural market analyst with access to real-time data.

TASK: Predict {crop_name} prices for the next {days_ahead} days based on comprehensive data analysis.

CROP DETAILS:
- Crop: {crop_name}
- User's Reference Price: ₹{current_price} per quintal
- Location: {location}
- Analysis Date: {datetime.now().strftime('%Y-%m-%d')}

{weather_context}

{market_intelligence}

ANALYSIS INSTRUCTIONS:
1. Use the ACTUAL CURRENT MARKET PRICE from online data if available, not the user's reference price
2. Factor in current weather conditions and forecast for crop health and harvest
3. Consider recent news and market conditions
4. Analyze how weather (rain, temperature, humidity) will affect supply
5. Account for seasonal factors, demand patterns, and supply chain
6. Consider policy updates and their market impact

PROVIDE PREDICTION IN THIS EXACT FORMAT:
DAY_7_PRICE: [predicted price in rupees]
DAY_15_PRICE: [predicted price in rupees]
DAY_30_PRICE: [predicted price in rupees]
TREND: [UPWARD/DOWNWARD/STABLE]
CONFIDENCE: [HIGH/MEDIUM/LOW]
PEAK_DAY: [day number 1-30 when price will be highest]
LOWEST_DAY: [day number 1-30 when price will be lowest]
KEY_FACTORS:
- [Factor 1 based on weather/news/market data]
- [Factor 2]
- [Factor 3]
- [Factor 4]
- [Factor 5]
RECOMMENDATION: [Specific actionable advice for farmer based on all data]

Be realistic and data-driven. If online price differs from user's reference, explain why in recommendation."""

        try:
            print("🤖 AI is analyzing all data and generating predictions...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            prediction = self._parse_prediction_response(response.text, current_price)
            
            # Add weather and market data to prediction
            prediction['weather_data'] = weather_data
            prediction['online_data'] = online_data
            prediction['cached'] = False
            prediction['generated_at'] = datetime.now().isoformat()
            
            # Cache the prediction for 24 hours
            self.cache.set_prediction_cache(crop_name, location, current_price, prediction, hours=24)
            print("💾 Prediction cached for 24 hours")
            
            print("✅ Prediction complete!")
            return prediction
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Unable to generate price prediction'
            }
    
    def _parse_prediction_response(self, response_text, current_price):
        """Parse AI's prediction response into structured data."""
        
        lines = response_text.strip().split('\n')
        prediction = {
            'success': True,
            'current_price': current_price,
            'predictions': {},
            'trend': 'STABLE',
            'confidence': 'MEDIUM',
            'peak_day': 30,
            'lowest_day': 1,
            'key_factors': [],
            'recommendation': '',
            'raw_response': response_text
        }
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('DAY_7_PRICE:'):
                price = self._extract_price(line)
                prediction['predictions']['day_7'] = price
            
            elif line.startswith('DAY_15_PRICE:'):
                price = self._extract_price(line)
                prediction['predictions']['day_15'] = price
            
            elif line.startswith('DAY_30_PRICE:'):
                price = self._extract_price(line)
                prediction['predictions']['day_30'] = price
            
            elif line.startswith('TREND:'):
                trend = line.split(':', 1)[1].strip().upper()
                if trend in ['UPWARD', 'DOWNWARD', 'STABLE']:
                    prediction['trend'] = trend
            
            elif line.startswith('CONFIDENCE:'):
                confidence = line.split(':', 1)[1].strip().upper()
                if confidence in ['HIGH', 'MEDIUM', 'LOW']:
                    prediction['confidence'] = confidence
            
            elif line.startswith('PEAK_DAY:'):
                try:
                    peak = int(self._extract_number(line))
                    prediction['peak_day'] = peak
                except:
                    pass
            
            elif line.startswith('LOWEST_DAY:'):
                try:
                    lowest = int(self._extract_number(line))
                    prediction['lowest_day'] = lowest
                except:
                    pass
            
            elif line.startswith('KEY_FACTORS:'):
                # Next few lines are factors
                continue
            
            elif line.startswith('-') or line.startswith('•'):
                # Factor bullet point
                factor = line.lstrip('-•').strip()
                if factor and len(prediction['key_factors']) < 5:
                    prediction['key_factors'].append(factor)
            
            elif line.startswith('RECOMMENDATION:'):
                prediction['recommendation'] = line.split(':', 1)[1].strip()
        
        # Calculate price change percentages
        if 'day_30' in prediction['predictions']:
            prediction['price_change_30d'] = round(
                ((prediction['predictions']['day_30'] - current_price) / current_price) * 100, 2
            )
        
        return prediction
    
    def _extract_price(self, text):
        """Extract numeric price from text."""
        import re
        # Find numbers in the text
        numbers = re.findall(r'[\d,]+\.?\d*', text.replace('₹', '').replace(',', ''))
        if numbers:
            return float(numbers[0])
        return 0.0
    
    def _extract_number(self, text):
        """Extract first number from text."""
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            return numbers[0]
        return '0'
    
    def get_best_selling_time(self, crop_name, current_price, harvest_date=None):
        """
        Determine the best time to sell the crop for maximum profit.
        
        Args:
            crop_name: Name of the crop
            current_price: Current market price
            harvest_date: Expected harvest date (optional)
        
        Returns:
            dict: Best selling recommendations
        """
        
        harvest_info = ""
        if harvest_date:
            harvest_info = f"Expected harvest date: {harvest_date}"
        
        prompt = f"""You are an agricultural marketing expert specializing in Indian markets.

TASK: Advise farmer on BEST TIME TO SELL their crop.

CROP DETAILS:
- Crop: {crop_name}
- Current Market Price: ₹{current_price} per quintal
{harvest_info}
- Current Date: {datetime.now().strftime('%Y-%m-%d')}

ANALYSIS REQUIRED:
Consider these factors:
1. Seasonal demand peaks (festivals, wedding season, holidays)
2. Historical price patterns for {crop_name}
3. Storage costs vs price appreciation
4. Market surplus/shortage periods
5. Weather patterns affecting supply

PROVIDE ADVICE IN THIS EXACT FORMAT:
BEST_MONTH: [month name]
BEST_REASON: [2-3 sentences why]
SELL_NOW_SCORE: [0-10 score]
WAIT_SCORE: [0-10 score]
STORAGE_ADVICE: [practical storage tips]
EXPECTED_PEAK_PRICE: [estimated price]
RISK_FACTORS: [3 bullet points]
ACTION: [SELL_NOW/WAIT_FOR_BETTER_PRICE/SELL_PARTIALLY]
TIMELINE: [specific timeframe recommendation]

Be practical and consider farmer's perspective (storage costs, urgent cash needs, perishability)."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            advice = self._parse_selling_advice(response.text)
            return advice
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Unable to generate selling advice'
            }
    
    def _parse_selling_advice(self, response_text):
        """Parse selling time advice from AI response."""
        
        lines = response_text.strip().split('\n')
        advice = {
            'success': True,
            'best_month': '',
            'reason': '',
            'sell_now_score': 5,
            'wait_score': 5,
            'storage_advice': '',
            'expected_peak_price': 0.0,
            'risk_factors': [],
            'action': 'WAIT_FOR_BETTER_PRICE',
            'timeline': '',
            'raw_response': response_text
        }
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('BEST_MONTH:'):
                advice['best_month'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('BEST_REASON:'):
                advice['reason'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('SELL_NOW_SCORE:'):
                try:
                    score = int(self._extract_number(line))
                    advice['sell_now_score'] = min(10, max(0, score))
                except:
                    pass
            
            elif line.startswith('WAIT_SCORE:'):
                try:
                    score = int(self._extract_number(line))
                    advice['wait_score'] = min(10, max(0, score))
                except:
                    pass
            
            elif line.startswith('STORAGE_ADVICE:'):
                advice['storage_advice'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('EXPECTED_PEAK_PRICE:'):
                advice['expected_peak_price'] = self._extract_price(line)
            
            elif line.startswith('RISK_FACTORS:'):
                continue
            
            elif line.startswith('-') or line.startswith('•'):
                factor = line.lstrip('-•').strip()
                if factor and len(advice['risk_factors']) < 5:
                    advice['risk_factors'].append(factor)
            
            elif line.startswith('ACTION:'):
                action = line.split(':', 1)[1].strip().upper()
                if action in ['SELL_NOW', 'WAIT_FOR_BETTER_PRICE', 'SELL_PARTIALLY']:
                    advice['action'] = action
            
            elif line.startswith('TIMELINE:'):
                advice['timeline'] = line.split(':', 1)[1].strip()
        
        return advice
    
    def calculate_profit(self, crop_name, expected_price, actual_price, quantity, unit="quintal"):
        """
        Calculate profit/loss comparing expected vs actual prices.
        
        Args:
            crop_name: Name of the crop
            expected_price: Expected selling price
            actual_price: Actual selling price
            quantity: Quantity sold
            unit: Unit of measurement (default: quintal)
        
        Returns:
            dict: Detailed profit calculation
        """
        
        # Calculate basic profit
        expected_revenue = expected_price * quantity
        actual_revenue = actual_price * quantity
        profit_loss = actual_revenue - expected_revenue
        profit_percentage = ((actual_price - expected_price) / expected_price) * 100 if expected_price > 0 else 0
        
        # Get AI analysis for context
        prompt = f"""You are a farm business analyst.

TRANSACTION ANALYSIS:
- Crop: {crop_name}
- Expected Price: ₹{expected_price} per {unit}
- Actual Price: ₹{actual_price} per {unit}
- Quantity: {quantity} {unit}
- Profit/Loss: ₹{profit_loss}
- Percentage: {profit_percentage:.2f}%

Provide brief analysis in this format:
VERDICT: [GOOD_DEAL/FAIR_DEAL/POOR_DEAL/LOSS]
ANALYSIS: [2-3 sentences explaining the result]
MARKET_CONTEXT: [Was market up/down? Why?]
LEARNING: [One key lesson for future]"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            analysis_lines = response.text.strip().split('\n')
            
            verdict = 'FAIR_DEAL'
            analysis = ''
            market_context = ''
            learning = ''
            
            for line in analysis_lines:
                if line.startswith('VERDICT:'):
                    verdict = line.split(':', 1)[1].strip()
                elif line.startswith('ANALYSIS:'):
                    analysis = line.split(':', 1)[1].strip()
                elif line.startswith('MARKET_CONTEXT:'):
                    market_context = line.split(':', 1)[1].strip()
                elif line.startswith('LEARNING:'):
                    learning = line.split(':', 1)[1].strip()
            
        except:
            verdict = 'GOOD_DEAL' if profit_loss >= 0 else 'LOSS'
            analysis = f"You made ₹{abs(profit_loss):.2f} {'profit' if profit_loss >= 0 else 'loss'} on this transaction."
            market_context = "Market analysis unavailable"
            learning = "Compare prices before selling"
        
        return {
            'success': True,
            'crop_name': crop_name,
            'expected_price': expected_price,
            'actual_price': actual_price,
            'quantity': quantity,
            'unit': unit,
            'expected_revenue': round(expected_revenue, 2),
            'actual_revenue': round(actual_revenue, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_percentage': round(profit_percentage, 2),
            'verdict': verdict,
            'analysis': analysis,
            'market_context': market_context,
            'learning': learning
        }


