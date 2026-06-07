import requests

def get_weather(city):
    """Get current weather for a city using free API"""
    try:
        # Free weather API (no API key required)
        url = f"https://wttr.in/{city}?format=%C+%t+%w"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            weather_text = response.text.strip()
            # Example output: "Partly cloudy +25°C 15 km/h"
            return f"Weather in {city}: {weather_text}"
        else:
            return f"Could not get weather for {city}"
    except Exception as e:
        return f"Weather error: {e}"