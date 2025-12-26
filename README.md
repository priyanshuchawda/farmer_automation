# Smart Farmer Marketplace 🌾

A Streamlit web application that empowers farmers with a marketplace for tools and crops, AI-powered insights, and smart weather integration.

## 🚀 Features

*   **Marketplace**: Rent farming tools and sell crops directly.
*   **AI Integration**: Get farming advice and listing recommendations using Google AI.
*   **Smart Calendar**: Plan farming activities with weather-aware event scheduling.
*   **Weather Forecasting**: Real-time and ML-predicted weather for accurate planning.
*   **Farmer Profiles**: Personalized experience based on location and farm details.
*   **Multilingual Support**: Accessible in multiple languages.

## 📂 Project Structure

```
farmer/
├── app.py              # Main application entry point
├── assets/             # Static assets
├── components/         # UI components and pages
├── database/           # Database modules and logic
├── docs/               # Documentation
│   ├── guides/         # User and Developer guides
│   └── archive/        # Historical project logs
├── scripts/            # Utility and maintenance scripts
├── tests/              # Unit tests
├── weather/            # Weather forecasting modules
└── farmermarket.db     # SQLite Database
```

## 🛠️ Getting Started

### Prerequisites

*   Python 3.8+
*   Pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your_username/SmartFarmerMarketplace.git
    cd SmartFarmerMarketplace
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup:**
    Create a `.env` file in the root directory:
    ```env
    AI_API_KEY=your_google_ai_key
    OPENWEATHER_API_KEY=your_openweather_key
    ```

### Running the App

```bash
streamlit run app.py
```

## 📖 Documentation

*   [Implementation Guides](docs/guides/)
*   [Weather System](docs/guides/weather_README.md)
*   [Calendar Features](docs/guides/CALENDAR_USER_GUIDE.md)

## 🔧 Scripts & Maintenance

Utility scripts are located in `scripts/`. To run them, ensure you are in the root directory or adjust paths accordingly.

*   `python scripts/populate_database.py`: Add sample data.
*   `python scripts/migrate_db.py`: Run database migrations.

## 🤝 Contributing

Contributions are welcome! Please check the `docs/` folder for architectural details.

---
*Built for the Smart India Hackathon 2024*