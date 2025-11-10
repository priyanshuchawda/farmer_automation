"""
Test script for Voice Listing Creator
Tests the Gemini API integration and structured output
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional, Literal
import json

# Load environment variables
load_dotenv()

# Pydantic models
class ToolListing(BaseModel):
    """Schema for Tool/Machine listing"""
    farmer_name: Optional[str] = Field(description="Name of the farmer")
    location: Optional[str] = Field(description="Village or location name")
    tool_type: Optional[Literal["Tractor", "Plow", "Seeder", "Sprayer", "Harvester", "Other"]] = Field(
        description="Type of farm tool or machine"
    )
    rent_rate: Optional[float] = Field(description="Rent rate per day in rupees")
    contact: Optional[str] = Field(description="Contact phone number (10 digits)")
    notes: Optional[str] = Field(description="Additional notes")


class CropListing(BaseModel):
    """Schema for Crop listing"""
    farmer_name: Optional[str] = Field(description="Name of the farmer")
    location: Optional[str] = Field(description="Village or location name")
    crop_name: Optional[str] = Field(description="Name of the crop")
    quantity: Optional[float] = Field(description="Quantity in numeric value")
    unit: Optional[Literal["Quintals", "Kilograms", "Tonnes"]] = Field(
        description="Unit of measurement"
    )
    price_per_unit: Optional[float] = Field(description="Expected price per unit in rupees")
    contact: Optional[str] = Field(description="Contact phone number (10 digits)")


def test_text_based_extraction():
    """
    Test the structured extraction with text input
    (simulating what the audio transcription would produce)
    """
    print("=" * 60)
    print("🧪 Testing Voice Listing Feature (Text-based simulation)")
    print("=" * 60)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file!")
        print("Please add your Gemini API key to .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    client = genai.Client(api_key=api_key)
    
    # Test Case 1: Hindi Tool Listing
    print("\n" + "=" * 60)
    print("Test 1: Hindi Tool Listing (Tractor)")
    print("=" * 60)
    
    hindi_text = """
    Mera naam Ramesh Kumar hai. Main Wagholi gaon se hu. 
    Mere paas ek tractor hai jo main kiraye par dena chahta hu. 
    Ek din ka 2000 rupay hai. Tractor bilkul naya hai, achi condition mein hai.
    Mera phone number 9876543210 hai.
    """
    
    prompt = """
    You are an AI assistant helping farmers create tool/machine rental listings.
    Extract the following information from the text in Hindi or English:
    
    - Farmer's name (किसान का नाम)
    - Location/Village (गांव)
    - Tool/Machine type (औजार)
    - Rent rate per day in rupees (किराया प्रति दिन)
    - Contact number (फोन नंबर)
    - Any additional notes (अतिरिक्त जानकारी)
    
    Return ONLY valid JSON matching the schema. If information is missing, use null.
    Be smart about extracting tool type - map variations to: Tractor, Plow, Seeder, Sprayer, Harvester, or Other.
    Extract 10-digit phone numbers even if spaces/dashes are present.
    
    Text: """ + hindi_text
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=ToolListing.model_json_schema(),
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        
        result = json.loads(response.text)
        print("\n✅ Extraction successful!")
        print("\n📋 Extracted Data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Validate
        tool = ToolListing(**result)
        print("\n✅ Schema validation passed!")
        print(f"   Farmer: {tool.farmer_name}")
        print(f"   Location: {tool.location}")
        print(f"   Tool: {tool.tool_type}")
        print(f"   Rate: ₹{tool.rent_rate}/day")
        print(f"   Contact: {tool.contact}")
        
    except Exception as e:
        print(f"\n❌ Test 1 Failed: {str(e)}")
        return False
    
    # Test Case 2: Marathi Crop Listing
    print("\n" + "=" * 60)
    print("Test 2: Marathi Crop Listing (Tomato)")
    print("=" * 60)
    
    marathi_text = """
    नमस्कार, माझे नाव सुरेश पाटील आहे. मी शिरूर गावातून आहे.
    माझ्याकडे 100 quintal टोमॅटो आहे विकायला.
    20 रुपये किलो मला हवे आहेत. फोन नंबर 9823456789.
    """
    
    prompt = """
    You are an AI assistant helping farmers create crop sale listings.
    Extract the following information from the text in Marathi or English:
    
    - Farmer's name (शेतकऱ्याचे नाव)
    - Location/Village (गाव)
    - Crop name (पिकाचे नाव)
    - Quantity (प्रमाण)
    - Unit: Quintals, Kilograms, or Tonnes (एकक)
    - Price per unit in rupees (किंमत प्रति एकक)
    - Contact number (दूरध्वनी क्रमांक)
    
    Return ONLY valid JSON matching the schema. If information is missing, use null.
    Common Marathi crop names: गहू (Wheat), तांदूळ (Rice), टोमॅटो (Tomato).
    Extract 10-digit phone numbers even if spaces/dashes are present.
    
    Text: """ + marathi_text
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=CropListing.model_json_schema(),
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        
        result = json.loads(response.text)
        print("\n✅ Extraction successful!")
        print("\n📋 Extracted Data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Validate
        crop = CropListing(**result)
        print("\n✅ Schema validation passed!")
        print(f"   Farmer: {crop.farmer_name}")
        print(f"   Location: {crop.location}")
        print(f"   Crop: {crop.crop_name}")
        print(f"   Quantity: {crop.quantity} {crop.unit}")
        print(f"   Price: ₹{crop.price_per_unit}/{crop.unit}")
        print(f"   Contact: {crop.contact}")
        
    except Exception as e:
        print(f"\n❌ Test 2 Failed: {str(e)}")
        return False
    
    # Test Case 3: English Mixed with Hindi
    print("\n" + "=" * 60)
    print("Test 3: Mixed Language Crop Listing (Wheat)")
    print("=" * 60)
    
    mixed_text = """
    Hello, my name is Vijay Singh. Main Pune ke paas Khed gaon se hu.
    I have 50 tonnes of wheat for sale. Price is 2500 rupees per quintal.
    Good quality wheat. Contact number nau aath do char panch cha sat aath nau do.
    """
    
    prompt = """
    You are an AI assistant helping farmers create crop sale listings.
    Extract the following information from the text (may be in English, Hindi, or mixed):
    
    - Farmer's name
    - Location/Village
    - Crop name
    - Quantity
    - Unit: Quintals, Kilograms, or Tonnes
    - Price per unit in rupees
    - Contact number (extract from words like "nau aath do" = 982)
    
    Return ONLY valid JSON matching the schema. If information is missing, use null.
    Extract 10-digit phone numbers even if spoken as words.
    
    Text: """ + mixed_text
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=CropListing.model_json_schema(),
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        
        result = json.loads(response.text)
        print("\n✅ Extraction successful!")
        print("\n📋 Extracted Data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Validate
        crop = CropListing(**result)
        print("\n✅ Schema validation passed!")
        print(f"   Farmer: {crop.farmer_name}")
        print(f"   Location: {crop.location}")
        print(f"   Crop: {crop.crop_name}")
        print(f"   Quantity: {crop.quantity} {crop.unit}")
        print(f"   Price: ₹{crop.price_per_unit}/{crop.unit}")
        print(f"   Contact: {crop.contact}")
        
    except Exception as e:
        print(f"\n❌ Test 3 Failed: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n🎉 Voice Listing Feature is ready to use!")
    print("\nNext steps:")
    print("1. The feature can now process audio with Gemini 2.5 Flash")
    print("2. It will transcribe speech in Hindi/Marathi/English")
    print("3. It will extract structured data automatically")
    print("4. Users can review and correct before submitting")
    print("\n" + "=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_text_based_extraction()
    if not success:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        exit(1)
    else:
        print("\n✅ Ready to integrate with the main app!")
        exit(0)
