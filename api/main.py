from fastapi import FastAPI, Depends,HTTPException
import requests
import os
import logging


app = FastAPI()

# Load your OpenWeatherMap API key from environment variables
# Define a dependency to retrieve the API key
def get_api_key():
    API_KEY = os.getenv("WEATHER_API_KEY")
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key not found.")
    
    logging.info(f"API Key loaded: {API_KEY[:4]}... [truncated for security]")

    return API_KEY

@app.get("/")
async def health_check():
    return {"message": "Welcome to the Weather API demo for TRACR - we are up and running..."}

@app.get("/weather")
async def get_weather(city: str, api_key: str = Depends(get_api_key)):

    # If no city is provided, return helpful information
    if not city:
        return {
            "error": "Missing required query parameter: 'city'.",
            "usage": "Please provide the 'city' parameter to fetch weather information.",
            "example": "/weather?city=New York",
            "parameters": {
                "city": "The name of the city (e.g., 'New York')."
            }
        }

    try:
        # Step 1: Get latitude and longitude for the city
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        geo_response = requests.get(geo_url)

        if geo_response.status_code != 200:
            raise HTTPException(status_code=geo_response.status_code, detail="Error retrieving location details.")

        geo_data = geo_response.json()

        if not geo_data:
            raise HTTPException(status_code=404, detail="City not found.")

        # Extract latitude and longitude
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Step 2: Get weather details using latitude and longitude
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}"
        weather_response = requests.get(weather_url)

        if weather_response.status_code != 200:
            weather_response.reason
            raise HTTPException(status_code=weather_response.status_code, detail=weather_response.reason + " " + "Lat= " + str(lat) + " " + "Lon= " + str(lon))

        weather_data = weather_response.json()

        # Step 3: Return the weather data as a JSON response
        return {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "current_weather": weather_data.get("current", {}),
            "daily_forecast": weather_data.get("daily", [])
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")




