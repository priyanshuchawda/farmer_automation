# Smart Farmer Marketplace

A Streamlit web application that provides a marketplace for farmers to list and rent out their tools and sell their crops. The application also features AI-powered recommendations using the Google Gemini API.

## About the Project

This project is a prototype for a smart marketplace that aims to connect farmers and empower them with data-driven insights. It is built with Python and Streamlit, and it uses a SQLite database to store the data.

## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

You will need to have Python and pip installed on your system.

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/your_username_/SmartFarmerMarketplace.git
    ```
2.  Install the required packages
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the root of the project.
2.  Add your API keys to the `.env` file:
    ```
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    OPENWEATHER_API_KEY=YOUR_OPENWEATHER_API_KEY
    ```
    - Get your Gemini API key from: https://makersuite.google.com/app/apikey
    - Get your OpenWeather API key from: https://openweathermap.org/api

## Usage

To run the application, use the following command:

```sh
streamlit run app.py
```

## Database

The application uses a SQLite database named `farmermarket.db`. The database has the following tables:

-   **tools**: Stores information about the tools available for rent.
    -   `Farmer` (TEXT)
    -   `Location` (TEXT)
    -   `Tool` (TEXT)
    -   `Rate` (REAL)
    -   `Contact` (TEXT)
    -   `Notes` (TEXT)
-   **crops**: Stores information about the crops available for sale.
    -   `Farmer` (TEXT)
    -   `Location` (TEXT)
    -   `Crop` (TEXT)
    -   `Quantity` (TEXT)
    -   `Expected_Price` (REAL)
    -   `Contact` (TEXT)
    -   `Listing_Date` (TEXT)
-   **farmers**: Stores information about the farmers.
    -   `name` (TEXT)
    -   `location` (TEXT)
    -   `farm_size` (REAL)
    -   `farm_unit` (TEXT)
    -   `contact` (TEXT)

## Features

-   **User Roles:** The application has two user roles: "Farmer" and "Admin".
-   **Farmer View:** Farmers can log in, add new tool and crop listings, and view all listings.
-   **Admin View:** Admins can do everything a farmer can do, plus they can view the database tables and add new farmer profiles.
-   **AI Recommendations:** The application provides AI-powered recommendations to farmers when they add a new listing.
-   **Profile Integration:** The application pre-fills the listing forms with the farmer's information if they have a profile in the database.
-   **Weather Forecast:** Integrated weather forecasting system that combines ML models with real-time API data for accurate predictions.
-   **Farmer Calendar:** Calendar component for tracking important farming events and dates.

## 🌟 Advanced Features

### 1. Weather Integration
The weather module provides intelligent weather forecasting using:
- **Machine Learning Models:** XGBoost, Random Forest, and Linear Regression ensemble for Pune
- **OpenWeather API:** Real-time weather data for any city worldwide
- **Gemini AI:** Natural language query processing + farming advice
- **Hybrid Predictions:** Weighted combination of ML models and API data for optimal accuracy

Features:
- Multi-city weather support
- Natural language queries (e.g., "weather in Mumbai tomorrow")
- 5-7 day forecasts with farming recommendations
- Personalized weather based on farmer's profile location
- Temperature, rainfall, and wind speed predictions

### 2. Smart Calendar with AI & Weather Alerts
The integrated calendar system combines AI planning with real-time weather data:

Features:
- **AI-Powered Planning:** Generate farming schedules using Gemini AI
- **Weather-Integrated Events:** Automatic weather alerts for each calendar event
- **Location-Based Forecasts:** Uses farmer's profile location for personalized weather
- **Smart Recommendations:** Get farming advice based on weather conditions
- **Database Persistence:** All events saved to SQLite database

### 3. Farmer Profile System
Complete profile management with weather integration:

Features:
- **Profile Creation:** Store farmer details (name, location, farm size, contact)
- **Weather Location:** Set preferred location for weather forecasts
- **Auto-Coordinates:** Automatic lat/long lookup using Gemini + Google Search
- **Calendar Integration:** Profile location used for calendar weather alerts
- **Data Persistence:** All profiles stored in SQL database

## 🔄 Complete Integration Flow

```
Farmer Login → Profile (with weather location) → Calendar Events
                     ↓                                    ↓
                Weather API ←→ Weather Alerts → Event Planning
                     ↓
              Gemini AI Advice → Farming Recommendations
```

### How It Works:
1. **Farmer creates profile** with farm location and weather location
2. **System fetches coordinates** for weather location using Gemini AI + Google Search
3. **Weather data is retrieved** from OpenWeather API using coordinates
4. **Calendar events get weather alerts** automatically based on event date
5. **AI generates farming plans** that can be added to calendar with weather alerts
6. **Gemini provides farming advice** based on current weather conditions
