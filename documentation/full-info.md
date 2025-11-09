# Project Overview: Smart Farmer Marketplace

This document provides a brief overview of the "Smart Farmer Marketplace" project, outlining its features, technology stack, and overall purpose.

## Purpose

The "Smart Farmer Marketplace" is a Streamlit web application designed to empower farmers by providing a platform to list and rent out their tools, sell their crops, and access data-driven insights. It aims to connect farmers and streamline various aspects of their agricultural operations.

## Key Features

*   **User Roles:** Differentiated access for "Farmer" and "Admin" users.
*   **Marketplace Functionality:**
    *   Farmers can create listings for tools available for rent.
    *   Farmers can create listings for crops available for sale.
*   **AI-Powered Recommendations:** Provides intelligent recommendations to farmers, particularly when creating new listings.
*   **Farmer Profile Integration:** Automatically pre-fills listing forms with farmer-specific information from their profiles.
*   **Advanced Weather Integration:**
    *   **Intelligent Forecasting:** Utilizes an ensemble of Machine Learning models (XGBoost, Random Forest, Linear Regression) combined with real-time data from the OpenWeather API for accurate predictions.
    *   **Multi-City Support:** Provides weather forecasts for various locations.
    *   **Natural Language Queries:** Users can query weather information using natural language (e.g., "weather in Mumbai tomorrow").
    *   **Detailed Forecasts:** Offers 5-7 day forecasts, including farming-specific recommendations.
    *   **Personalized Weather:** Tailors weather information based on the farmer's registered profile location.
    *   **Data Points:** Predicts temperature, rainfall, and wind speed.
*   **Smart Calendar System:**
    *   **AI-Powered Planning:** Assists in generating optimized farming schedules using AI.
    *   **Weather-Integrated Events:** Automatically links weather alerts to calendar events, providing timely notifications.
    *   **Location-Based Forecasts:** Uses the farmer's profile location to provide relevant weather data for calendar events.
    *   **Smart Recommendations:** Offers farming advice contextualized by current and forecasted weather conditions.
    *   **Data Persistence:** All calendar events are securely stored in the SQLite database.
*   **Comprehensive Farmer Profile System:**
    *   **Profile Creation:** Allows farmers to store essential details such as name, location, farm size, and contact information.
    *   **Weather Location Setting:** Farmers can specify a preferred location for weather forecasts.
    *   **Automated Geo-coding:** Automatically determines latitude and longitude coordinates for locations using AI and Google Search.
    *   **Calendar Integration:** Profile location is utilized for personalized weather alerts within the calendar.
    *   **Data Persistence:** All farmer profiles are stored in the SQLite database.

## Technology Stack

*   **Frontend Framework:** Streamlit (Python)
*   **Backend Logic:** Python
*   **Database:** SQLite (`farmermarket.db`)
*   **Artificial Intelligence/Machine Learning:**
    *   Google AI API
    *   `scikit-learn`
    *   `xgboost`
    *   `joblib`
    *   `numpy`
    *   `pandas`
*   **External APIs:**
    *   Google AI API
    *   OpenWeather API
*   **Other Python Libraries:**
    *   `python-dotenv` (for environment variable management)
    *   `requests` (for HTTP requests)
    *   `plotly` (for data visualization)
    *   `pydantic` (for data validation)

## High-Level Project Structure

*   `app.py`: The main entry point for the Streamlit application.
*   `components/`: Contains modular Streamlit components and pages (e.g., AI chatbot, authentication, market price display, weather, calendar integration).
*   `ai/`: Houses modules related to AI functionalities, such as AI matching and price prediction.
*   `database/`: Manages database interactions, including cache management and core database functions.
*   `weather/`: Dedicated modules for weather forecasting, API interactions, and enhanced weather models.
*   `calender/`: Contains components and logic for the calendar system, including day and week views.
*   `documentation/`: Stores all project documentation and markdown files.
*   `tests/`: Contains all unit and integration test files for the project.
