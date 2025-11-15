"""
Climate Risk Analyzer - Core module for climate-resilience features
Uses Gemini AI with structured output for precise risk scoring
"""

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import os
from weather.api_client import OpenWeatherAPI

# Pydantic models for structured output
class DroughtRiskAssessment(BaseModel):
    """Structured drought risk assessment"""
    score: int = Field(description="Drought risk score from 0-100", ge=0, le=100)
    level: str = Field(description="Risk level: LOW, MODERATE, HIGH, or CRITICAL")
    days_without_rain: int = Field(description="Number of days since last significant rain")
    soil_moisture: int = Field(description="Estimated soil moisture percentage", ge=0, le=100)
    next_rain_days: int = Field(description="Days until next expected rain")
    temperature_stress: str = Field(description="Temperature stress level: NONE, MILD, MODERATE, or SEVERE")
    actions: List[str] = Field(description="List of specific recommended actions")
    estimated_loss_if_ignored: Optional[str] = Field(description="Potential financial loss if no action taken")

class FloodRiskAssessment(BaseModel):
    """Structured flood risk assessment"""
    score: int = Field(description="Flood risk score from 0-100", ge=0, le=100)
    level: str = Field(description="Risk level: LOW, MODERATE, HIGH, or CRITICAL")
    upcoming_rain_3day: float = Field(description="Expected rainfall in next 3 days (mm)")
    soil_saturation: int = Field(description="Soil saturation percentage", ge=0, le=100)
    drainage_status: str = Field(description="Drainage condition: GOOD, FAIR, or POOR")
    actions: List[str] = Field(description="List of specific recommended actions")

class HeatStressAssessment(BaseModel):
    """Structured heat stress assessment"""
    score: int = Field(description="Heat stress score from 0-100", ge=0, le=100)
    level: str = Field(description="Risk level: LOW, MODERATE, HIGH, or CRITICAL")
    recent_max_temp: float = Field(description="Recent maximum temperature in Celsius")
    heat_wave_days: int = Field(description="Consecutive days above 35°C")
    crop_specific_impact: str = Field(description="Impact on specific crops grown")
    actions: List[str] = Field(description="List of specific recommended actions")

class ClimateAnalyzer:
    """
    Main Climate Risk Analyzer
    Calculates drought, flood, and heat stress risks using real weather data + AI analysis
    """
    
    def __init__(self, location: str, lat: float, lon: float):
        self.location = location
        self.lat = lat
        self.lon = lon
        self.weather_api = OpenWeatherAPI()
        
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
    
    def get_drought_risk(self) -> dict:
        """
        Calculate comprehensive drought risk using real weather data + AI
        Returns structured assessment with actionable recommendations
        """
        if not self.client:
            return self._fallback_drought_risk()
        
        try:
            # Get real weather data
            forecast = self.weather_api.get_detailed_forecast(self.lat, self.lon)
            
            if forecast is None or forecast.empty:
                return self._fallback_drought_risk()
            
            # Calculate metrics
            days_without_rain = self._count_dry_days(forecast)
            upcoming_rain = self._get_upcoming_rain(forecast)
            recent_temp = self._get_recent_max_temp(forecast)
            
            # Use Gemini AI with structured output for precise risk assessment
            prompt = f"""You are a climate risk analyst for farmers in India.

LOCATION: {self.location}
TODAY: {datetime.now().strftime('%Y-%m-%d')}

WEATHER DATA (Real-time from OpenWeather API):
- Days since last significant rain (>5mm): {days_without_rain} days
- Upcoming rain forecast (next 7 days): {upcoming_rain:.1f} mm
- Recent maximum temperature: {recent_temp:.1f}°C

TASK: Calculate drought risk score and provide specific actions

SCORING ALGORITHM:
Base Score = 0
+ Days without rain: 0-20 days (0 pts), 21-30 days (+20 pts), 31-45 days (+35 pts), 45+ days (+50 pts)
+ Low upcoming rain: <10mm (+30 pts), 10-25mm (+15 pts), >25mm (0 pts)  
+ High temperature: 30-35°C (+10 pts), 35-38°C (+20 pts), >38°C (+30 pts)

RISK LEVELS:
- 0-30: LOW
- 31-60: MODERATE  
- 61-80: HIGH
- 81-100: CRITICAL

Provide specific, actionable recommendations based on the risk level.
For HIGH/CRITICAL risk, estimate potential crop loss if farmer ignores warnings."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=DroughtRiskAssessment.model_json_schema(),
                    temperature=0.1  # Low temperature for consistent scoring
                )
            )
            
            # Parse structured response
            assessment = DroughtRiskAssessment.model_validate_json(response.text)
            
            return {
                'score': assessment.score,
                'level': assessment.level,
                'days_without_rain': assessment.days_without_rain,
                'soil_moisture': assessment.soil_moisture,
                'next_rain_days': assessment.next_rain_days,
                'temperature_stress': assessment.temperature_stress,
                'actions': assessment.actions,
                'estimated_loss': assessment.estimated_loss_if_ignored,
                'raw_data': {
                    'upcoming_rain_mm': upcoming_rain,
                    'recent_max_temp': recent_temp
                }
            }
            
        except Exception as e:
            print(f"Error in drought risk calculation: {e}")
            return self._fallback_drought_risk()
    
    def get_flood_risk(self) -> dict:
        """Calculate flood risk using weather forecast + AI"""
        if not self.client:
            return self._fallback_flood_risk()
        
        try:
            forecast = self.weather_api.get_detailed_forecast(self.lat, self.lon)
            
            if forecast is None or forecast.empty:
                return self._fallback_flood_risk()
            
            # Calculate 3-day rainfall
            upcoming_rain_3day = self._get_upcoming_rain(forecast, days=3)
            
            prompt = f"""You are a flood risk analyst for farmers in India.

LOCATION: {self.location}
TODAY: {datetime.now().strftime('%Y-%m-%d')}

WEATHER DATA:
- Rainfall forecast (next 3 days): {upcoming_rain_3day:.1f} mm
- Season: {self._get_current_season()}

SCORING:
Base Score = 0
+ Heavy rain forecast: 50-100mm (+30 pts), 100-150mm (+50 pts), >150mm (+70 pts)
+ Monsoon season active: Add +20 pts if heavy rain during monsoon

RISK LEVELS:
- 0-30: LOW
- 31-60: MODERATE
- 61-80: HIGH  
- 81-100: CRITICAL

Provide specific flood preparedness actions."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=FloodRiskAssessment.model_json_schema(),
                    temperature=0.1
                )
            )
            
            assessment = FloodRiskAssessment.model_validate_json(response.text)
            
            return {
                'score': assessment.score,
                'level': assessment.level,
                'upcoming_rain_3day': assessment.upcoming_rain_3day,
                'soil_saturation': assessment.soil_saturation,
                'drainage_status': assessment.drainage_status,
                'actions': assessment.actions
            }
            
        except Exception as e:
            print(f"Error in flood risk calculation: {e}")
            return self._fallback_flood_risk()
    
    def get_heat_stress(self, crop_type: str = "General crops") -> dict:
        """Calculate heat stress risk for specific crops"""
        if not self.client:
            return self._fallback_heat_stress()
        
        try:
            forecast = self.weather_api.get_detailed_forecast(self.lat, self.lon)
            
            if forecast is None or forecast.empty:
                return self._fallback_heat_stress()
            
            recent_max_temp = self._get_recent_max_temp(forecast)
            heat_wave_days = self._count_heat_wave_days(forecast)
            
            prompt = f"""You are an agricultural heat stress specialist.

LOCATION: {self.location}
CROP TYPE: {crop_type}
TODAY: {datetime.now().strftime('%Y-%m-%d')}

WEATHER DATA:
- Recent maximum temperature: {recent_max_temp:.1f}°C
- Consecutive hot days (>35°C): {heat_wave_days} days

CROP TEMPERATURE TOLERANCE (Reference):
- Tomato: Optimal 20-30°C, Stress >35°C
- Wheat: Optimal 15-25°C, Stress >30°C  
- Rice: Optimal 25-35°C, Stress >38°C
- Cotton: Optimal 25-35°C, Stress >40°C

SCORING:
Base Score = 0
+ Temperature: 30-33°C (+10 pts), 33-36°C (+25 pts), 36-39°C (+40 pts), >39°C (+60 pts)
+ Heat wave duration: 3-5 days (+15 pts), 5-7 days (+25 pts), >7 days (+35 pts)

Assess crop-specific heat stress and provide mitigation actions."""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=HeatStressAssessment.model_json_schema(),
                    temperature=0.1
                )
            )
            
            assessment = HeatStressAssessment.model_validate_json(response.text)
            
            return {
                'score': assessment.score,
                'level': assessment.level,
                'recent_max_temp': assessment.recent_max_temp,
                'heat_wave_days': assessment.heat_wave_days,
                'crop_impact': assessment.crop_specific_impact,
                'actions': assessment.actions
            }
            
        except Exception as e:
            print(f"Error in heat stress calculation: {e}")
            return self._fallback_heat_stress()
    
    def get_overall_risk(self) -> dict:
        """Get comprehensive climate risk summary"""
        drought = self.get_drought_risk()
        flood = self.get_flood_risk()
        heat = self.get_heat_stress()
        
        overall_score = (drought['score'] + flood['score'] + heat['score']) / 3
        
        # Determine highest risk
        risks = [
            ('Drought', drought['score'], drought['level']),
            ('Flood', flood['score'], flood['level']),
            ('Heat Stress', heat['score'], heat['level'])
        ]
        highest_risk = max(risks, key=lambda x: x[1])
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_level': self._get_risk_level(overall_score),
            'drought': drought,
            'flood': flood,
            'heat_stress': heat,
            'highest_risk': {
                'type': highest_risk[0],
                'score': highest_risk[1],
                'level': highest_risk[2]
            },
            'last_updated': datetime.now().isoformat()
        }
    
    # Helper methods
    def _count_dry_days(self, forecast) -> int:
        """Count consecutive days without significant rain"""
        dry_days = 0
        for _, row in forecast.iterrows():
            if row['rain'] < 2:  # Less than 2mm considered dry
                dry_days += 1
            else:
                break
        return min(dry_days, 60)  # Cap at 60 days
    
    def _get_upcoming_rain(self, forecast, days=7) -> float:
        """Sum rainfall for next N days"""
        if forecast.empty:
            return 0.0
        forecast_subset = forecast.head(days * 8)  # 8 readings per day (3-hour intervals)
        return forecast_subset['rain'].sum()
    
    def _get_recent_max_temp(self, forecast) -> float:
        """Get recent maximum temperature"""
        if forecast.empty:
            return 30.0
        return forecast.head(8)['temp'].max()  # Last 24 hours
    
    def _count_heat_wave_days(self, forecast) -> int:
        """Count consecutive days with temp > 35°C"""
        heat_days = 0
        daily_max_temps = []
        
        for i in range(0, min(len(forecast), 56), 8):  # Check 7 days, 8 readings/day
            day_data = forecast.iloc[i:i+8]
            daily_max = day_data['temp'].max()
            daily_max_temps.append(daily_max)
        
        for temp in daily_max_temps:
            if temp > 35:
                heat_days += 1
            else:
                break
        
        return heat_days
    
    def _get_current_season(self) -> str:
        """Determine current agricultural season in India"""
        month = datetime.now().month
        if month in [6, 7, 8, 9]:
            return "Monsoon (Kharif)"
        elif month in [10, 11, 12, 1, 2]:
            return "Winter (Rabi)"
        else:
            return "Summer (Zaid)"
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 30:
            return "MODERATE"
        else:
            return "LOW"
    
    # Fallback methods when AI or API fails
    def _fallback_drought_risk(self) -> dict:
        return {
            'score': 50,
            'level': 'MODERATE',
            'days_without_rain': 20,
            'soil_moisture': 50,
            'next_rain_days': 5,
            'temperature_stress': 'MILD',
            'actions': ['Monitor weather forecasts daily', 'Ensure irrigation is ready'],
            'estimated_loss': None,
            'raw_data': {}
        }
    
    def _fallback_flood_risk(self) -> dict:
        return {
            'score': 20,
            'level': 'LOW',
            'upcoming_rain_3day': 10.0,
            'soil_saturation': 40,
            'drainage_status': 'FAIR',
            'actions': ['Maintain drainage channels']
        }
    
    def _fallback_heat_stress(self) -> dict:
        return {
            'score': 30,
            'level': 'MODERATE',
            'recent_max_temp': 32.0,
            'heat_wave_days': 2,
            'crop_impact': 'Monitor crops for stress signs',
            'actions': ['Ensure adequate irrigation', 'Consider shade for sensitive crops']
        }
