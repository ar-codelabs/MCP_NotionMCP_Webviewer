"""
출장 준비를 위한 MCP 서버
"""
from mcp.server.fastmcp import FastMCP
from business_trip_tools import get_weather_info, get_country_info, get_season_info, calculate_trip_duration
import json

mcp = FastMCP(
    name="business-trip-server",
    instructions=(
        "You are a business trip preparation assistant. "
        "You help analyze destinations, weather, local requirements, and create comprehensive trip preparation guides."
    ),
)

@mcp.tool()
def get_destination_weather(destination: str, date: str = None) -> str:
    """
    Get weather information for a destination.
    
    Args:
        destination: The destination city or country
        date: Optional date in YYYY-MM-DD format
    
    Returns:
        Weather information as JSON string
    """
    weather_info = get_weather_info(destination, date)
    return json.dumps(weather_info, ensure_ascii=False)

@mcp.tool()
def get_destination_info(destination: str) -> str:
    """
    Get basic country/destination information including voltage, currency, culture.
    
    Args:
        destination: The destination city or country
    
    Returns:
        Country information as JSON string
    """
    country_info = get_country_info(destination)
    return json.dumps(country_info, ensure_ascii=False)

@mcp.tool()
def get_seasonal_info(destination: str, date: str) -> str:
    """
    Get seasonal information for a destination on a specific date.
    
    Args:
        destination: The destination city or country
        date: Date in YYYY-MM-DD format
    
    Returns:
        Seasonal information as JSON string
    """
    season_info = get_season_info(destination, date)
    return json.dumps(season_info, ensure_ascii=False)

@mcp.tool()
def calculate_duration(start_date: str, end_date: str) -> str:
    """
    Calculate trip duration in days.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Duration in days as string
    """
    duration = calculate_trip_duration(start_date, end_date)
    return str(duration)

@mcp.tool()
def analyze_business_culture(destination: str, purpose: str) -> str:
    """
    Analyze business culture and dress code requirements for a destination.
    
    Args:
        destination: The destination city or country
        purpose: Purpose of the trip (meeting, conference, etc.)
    
    Returns:
        Business culture analysis as JSON string
    """
    country_info = get_country_info(destination)
    
    analysis = {
        "business_culture": country_info.get("business_culture", "business casual"),
        "recommended_attire": "business formal" if country_info.get("business_culture") == "보수적" else "business casual",
        "cultural_notes": f"Business culture in {destination} tends to be {country_info.get('business_culture', 'moderate')}",
        "meeting_etiquette": "Punctuality is important" if country_info.get("business_culture") == "보수적" else "Relaxed atmosphere",
        "language": country_info.get("language", "English")
    }
    
    return json.dumps(analysis, ensure_ascii=False)

@mcp.tool()
def get_packing_recommendations(destination: str, duration: str, purpose: str, season: str) -> str:
    """
    Get comprehensive packing recommendations based on trip details.
    
    Args:
        destination: The destination city or country
        duration: Trip duration in days
        purpose: Purpose of the trip
        season: Season information
    
    Returns:
        Packing recommendations as JSON string
    """
    country_info = get_country_info(destination)
    duration_days = int(duration) if duration.isdigit() else 3
    
    recommendations = {
        "clothing": {
            "business_attire": 2 if duration_days <= 3 else duration_days - 1,
            "casual_wear": 1 if duration_days <= 2 else 2,
            "underwear": duration_days + 1,
            "socks": duration_days + 1
        },
        "electronics": {
            "power_adapter": f"Required: {country_info.get('plug_type', 'Universal')} type",
            "voltage": country_info.get('voltage', '220V'),
            "phone_charger": "Essential",
            "laptop": "If needed for work"
        },
        "essentials": {
            "passport": "Required for international travel",
            "visa": "Check requirements",
            "currency": f"Local currency: {country_info.get('currency', 'USD')}",
            "insurance": "Travel insurance recommended"
        },
        "weather_specific": {
            "umbrella": "Recommended" if "rain" in season.lower() else "Optional",
            "jacket": "Required" if "cold" in season.lower() or "winter" in season.lower() else "Light jacket",
            "sunscreen": "Recommended" if "summer" in season.lower() else "Optional"
        }
    }
    
    return json.dumps(recommendations, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("Starting Business Trip MCP Server...")
    mcp.run(transport="stdio")