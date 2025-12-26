# 🗺️ Location Services Guide - Smart Farmer Marketplace

## Overview

The Smart Farmer Marketplace now features **Google Maps Grounding with Gemini 2.5 Flash**, providing powerful location-aware services to help farmers find nearby agricultural resources, services, and support.

---

## 🌟 Features

### 1. **Location Management**
- **Store GPS Coordinates**: Save your farm's precise location once and use it everywhere
- **Multiple Input Methods**:
  - Enter location name (e.g., "Wadgaon Sheri, Pune")
  - Use GPS coordinates directly
  - Browser GPS (coming soon)
- **Automatic Coordinate Lookup**: AI-powered location-to-coordinates conversion
- **Address Verification**: Gemini validates and provides full address details

### 2. **Google Maps Grounding**
- **Real-time location data** from Google Maps
- **Accurate place information** with ratings, reviews, and contact details
- **Up-to-date business hours** and availability
- **Direct Google Maps links** for navigation
- **250+ million places worldwide**

### 3. **Location Services Page**
Access through: **🗺️ Location Services → 🗺️ Nearby Places & Services**

#### Available Service Categories:

##### 🔍 **Nearby Places**
Quick searches for common locations:
- 🛒 Markets and Mandis
- 🌾 Agricultural Input Stores
- 🚜 Equipment Dealers
- ⛽ Petrol Pumps
- 🏦 Banks and ATMs
- 🍽️ Restaurants

##### 🏪 **Agricultural Services**
Find essential farming services:
- Seed and fertilizer stores
- Agricultural equipment dealers
- Cold storage facilities
- Processing units
- Soil testing labs
- Organic input suppliers

##### 🏥 **Veterinary Services**
Locate animal healthcare:
- Veterinary hospitals
- Animal dispensaries
- Emergency veterinary care
- Veterinary pharmacies

##### 🏛️ **Government Offices**
Find government services:
- Agriculture department offices
- Tehsil/Taluka offices
- Krishi Bhavan
- Agricultural extension centers
- Horticulture department
- Animal husbandry offices

##### 🎯 **Custom Search**
Create your own queries with:
- Custom search terms
- Optional ratings and reviews
- Opening hours information
- Distance filtering

---

## 📍 How to Set Up Your Location

### Initial Setup (During Registration)

1. **Register a New Account**
   - Go to registration page
   - Complete Steps 1-2 (Basic Info & Farm Details)
   - **Step 3: Weather Location Setup**
     - Enter your location (e.g., "Pune, Maharashtra")
     - System automatically fetches GPS coordinates
     - Coordinates saved to your profile

2. **Coordinates are Stored**
   - Latitude and Longitude saved in database
   - Used for all location-based features
   - No need to enter location again

### Update Location (Existing Users)

1. **Go to Profile**
   - Navigate to: **👤 My Account → 👤 My Profile**

2. **Location Settings Section**
   - See current location and coordinates
   - Click "🔄 Update Location"

3. **Choose Input Method**:

   **Option A: Enter Location Name**
   ```
   1. Type location (e.g., "Wadgaon Sheri, Pune")
   2. Click "🔍 Find Coordinates"
   3. System shows coordinates and address
   4. Click "💾 Save This Location"
   ```

   **Option B: Use GPS Coordinates**
   ```
   1. Enter Latitude (e.g., 18.5204)
   2. Enter Longitude (e.g., 73.8567)
   3. Click "📍 Verify & Get Address"
   4. System shows address from coordinates
   5. Enter a name for the location
   6. Click "💾 Save Location"
   ```

---

## 🔍 Using Location Services

### Quick Nearby Search

1. Go to **🗺️ Location Services**
2. See your current location displayed at top
3. Click any quick search button (e.g., "🛒 Markets")
4. View results with:
   - Place names
   - Google Maps links
   - Ratings and reviews
   - Contact information

### Agricultural Services Search

1. Navigate to **Agricultural Services** tab
2. Select service type from dropdown
3. Adjust search radius (1-50 km)
4. Click "🔍 Search Agricultural Services"
5. View detailed results with expandable cards

### Veterinary Services

1. Go to **Veterinary Services** tab
2. Select type of service needed
3. Click "🔍 Find Veterinary Services"
4. Get list with ratings and direct links

### Custom Search

1. Navigate to **Custom Search** tab
2. Enter your specific query
3. Examples:
   - "Best irrigation equipment dealers near me"
   - "Organic fertilizer suppliers within 20km"
   - "Dairy collection centers in my area"
4. Check optional filters:
   - Include ratings and reviews
   - Include opening hours
5. Click "🔍 Search Now"
6. View comprehensive results

---

## 💡 Search Tips for Best Results

### Be Specific
- ✅ "Agricultural seed stores near me"
- ❌ "stores near me"

### Add Distance
- ✅ "Veterinary clinics within 5km"
- ✅ "Markets within 10 miles"

### Include Criteria
- ✅ "Restaurants with good reviews"
- ✅ "Stores open now"
- ✅ "Places with parking"

### Use Local Terms
- ✅ "Mandi near me"
- ✅ "Krushi kendra nearby"
- ✅ "Shetkari sahakari nearby"

### Multiple Searches
- Try different terms if first search doesn't work
- Be more or less specific as needed

---

## 🔧 Technical Implementation

### Database Structure

```sql
-- Farmers table includes location fields
CREATE TABLE farmers (
    name TEXT PRIMARY KEY,
    location TEXT,
    farm_size REAL,
    farm_unit TEXT,
    contact TEXT,
    weather_location TEXT,
    latitude REAL,          -- GPS latitude
    longitude REAL,         -- GPS longitude
    password TEXT
)
```

### Google Maps Grounding API

```python
# Example: Find nearby places
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Find agricultural equipment dealers near me",
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_maps=types.GoogleMaps())],
        tool_config=types.ToolConfig(
            retrieval_config=types.RetrievalConfig(
                lat_lng=types.LatLng(
                    latitude=user_latitude,
                    longitude=user_longitude
                )
            )
        ),
    ),
)
```

### Response Structure

```python
# Grounding metadata includes:
- grounding_chunks: List of places found
  - maps.title: Place name
  - maps.uri: Google Maps URL
  - maps.place_id: Unique place identifier
- google_maps_widget_context_token: For rendering map widget
```

---

## 📊 Features by Module

### `location_manager.py`
- `LocationManager` class
  - `get_coordinates_from_location()`: Location name → GPS
  - `get_address_from_coordinates()`: GPS → Address
  - `find_nearby_places()`: Search with location context
  - `get_location_aware_recommendations()`: Personalized suggestions

### `location_services_page.py`
- Main UI for location services
- Tabbed interface for different services
- Quick search buttons
- Custom search functionality
- Attribution and tips

### `database/db_functions.py`
- `update_farmer_location()`: Save location to DB
- `get_farmer_profile()`: Retrieve location data

---

## 🌐 Supported Models

Google Maps Grounding works with:
- ✅ Gemini 2.5 Flash
- ✅ Gemini 2.5 Pro
- ✅ Gemini 2.5 Flash-Lite
- ✅ Gemini 2.0 Flash

---

## 💰 Pricing

- **$25 per 1,000 grounded prompts**
- **Free tier: 500 requests/day**
- Only counted when results include Google Maps sources
- Multiple queries in one request = 1 request

---

## 🚀 Future Enhancements

1. **Browser GPS Integration**
   - Real-time location from browser
   - One-click location updates

2. **Saved Places**
   - Save frequently visited locations
   - Quick access to important places

3. **Route Planning**
   - Plan trips to multiple locations
   - Optimize routes for efficiency

4. **Location History**
   - Track places you've searched
   - Revisit previous searches

5. **Offline Mode**
   - Cache recent searches
   - View saved places without internet

6. **Social Features**
   - Share locations with other farmers
   - Community-recommended places

---

## 📞 Support

For questions or issues with location services:
1. Check this guide first
2. Try the test script: `python test_google_maps_grounding.py`
3. Review error messages in the UI
4. Contact system administrator

---

## 🔒 Privacy & Data

### What We Store
- Your farm's GPS coordinates
- Location name/address
- Search history (optional)

### What We Don't Store
- Real-time movement data
- Personal location history outside the app
- Shared location data with third parties

### Data Usage
- Coordinates used only for your location-based features
- Never shared without permission
- Can be deleted from your profile anytime

---

## ✅ Benefits for Farmers

1. **Save Time**: Find services quickly without asking around
2. **Make Better Decisions**: See ratings and reviews before visiting
3. **Stay Informed**: Get accurate, up-to-date business information
4. **Plan Efficiently**: Know opening hours and distances before traveling
5. **Discover Resources**: Find new services you didn't know existed
6. **Get Help Faster**: Locate emergency services when needed

---

## 📱 Integration with Other Features

### Weather Forecasts
- Uses same coordinates for accurate weather
- Location-specific forecasts
- Automatic weather alerts

### Market Prices
- Location-aware market data
- Nearby mandi prices
- Regional price comparisons

### Calendar Events
- Add location to calendar events
- Weather alerts for event dates
- Location-based reminders

### AI Chatbot
- Location-aware recommendations
- Context-specific farming advice
- Personalized suggestions based on region

---

## 🎯 Best Practices

1. **Keep Location Updated**
   - Update if you move to a new farm
   - Verify coordinates periodically

2. **Use Specific Searches**
   - Better results with detailed queries
   - Include your requirements in search

3. **Check Multiple Sources**
   - Compare results from different searches
   - Verify important information directly

4. **Save Important Places**
   - Note down frequently needed locations
   - Keep contact numbers handy

5. **Provide Feedback**
   - Report incorrect information
   - Suggest improvements

---

## 📚 Additional Resources

- [Gemini API Documentation](https://ai.google.dev/)
- [Google Maps Grounding Guide](https://ai.google.dev/gemini-api/docs/grounding)
- [Smart Farmer Marketplace User Guide](./user_guide.md)

---

**Last Updated:** 2025-11-09  
**Version:** 1.0.0  
**Powered by:** Gemini 2.5 Flash + Google Maps Grounding
