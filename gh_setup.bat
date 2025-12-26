@echo off
echo Setting up GitHub repository details...

REM Edit repository description and homepage
gh repo edit --description "Smart Farmer Marketplace: AI-powered agricultural platform for tool renting, crop selling, and weather insights." --homepage "https://your-streamlit-app-url.com"

REM Add relevant topics
gh repo edit --add-topic "python" --add-topic "streamlit" --add-topic "agriculture" --add-topic "ai" --add-topic "sustainability" --add-topic "marketplace" --add-topic "weather-forecasting"

echo Done! Please ensure you have the GitHub CLI (gh) installed and authenticated.
pause
