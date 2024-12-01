from flask import Flask, request, jsonify
import aiohttp
import asyncio
from datetime import datetime
import populartimes
import pytz
from aiocache import Cache
from aiocache.decorators import cached
import logging
import re
import uuid
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wait_time_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set up an in-memory cache (Redis can be used for production)
cache = Cache(Cache.MEMORY)

# Validate API Key format
def validate_api_key(api_key):
    # Specific pattern for Google API Key
    api_key_pattern = r'^AIza[A-Za-z0-9_-]{35}$'
    return re.match(api_key_pattern, api_key) is not None

# Secure API Key handling
API_KEY = 'AIzaSyAdPSNAoMbA-InKeHDH1G-w_ctNmVaadRg'
if not validate_api_key(API_KEY):
    logger.critical("Invalid Google API Key")
    raise ValueError("Invalid Google API Key")

# Validate Place ID
def validate_place_id(place_id):
    # Validate Google Place ID format
    place_id_pattern = r'^ChI[A-Za-z0-9_-]+$'
    return (
        place_id is not None 
        and isinstance(place_id, str) 
        and re.match(place_id_pattern, place_id) is not None
    )

# Function to fetch place details from Google Places API
def fetch_place_details(place_id):
    """Fetch place details using requests instead of aiohttp for reliability"""
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,popular_times&key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching place details: {e}")
        raise

# Asynchronous function to get populartimes data and estimate wait time
@cached(ttl=864000)  # Cache the result for 10 days (864,000 seconds)
async def get_estimated_wait_time(place_id):
    # Validate place ID 
    if not validate_place_id(place_id):
        logger.error(f"Invalid place_id: {place_id}")
        raise ValueError("Invalid place ID")
    
    try:
        # Fetch place details
        place_details = fetch_place_details(place_id)
        
        # Fetch populartimes data
        try:
            data = populartimes.get_id(API_KEY, place_id)
        except Exception as populartimes_error:
            logger.error(f"Populartimes data fetch error: {populartimes_error}")
            raise RuntimeError("Unable to fetch populartimes data")

        # Validate data structure
        if not data or 'populartimes' not in data:
            logger.warning(f"No populartimes data available for place_id: {place_id}")
            return "No data available for estimated wait time", {}

        # Get current time in IST
        ist_timezone = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist_timezone)
        current_day = now.strftime('%A')
        current_hour = now.hour

        # Find popular times for current day
        popular_times_data = None
        for day_data in data.get('populartimes', []):
            if day_data.get('name') == current_day:
                popular_times_data = day_data.get('data', [])
                break

        if not popular_times_data or current_hour is None:
            logger.warning(f"No popular times data for {current_day}")
            return "No data available for estimated wait time", {}

        # Mapping busy percentage to wait time
        def map_busy_percentage(busy_percentage):
            try:
                busy_percentage = float(busy_percentage)
            except (TypeError, ValueError):
                logger.warning(f"Invalid busy percentage: {busy_percentage}")
                return 0

            # Categorize busy percentage
            busy_categories = [
                (0, 20, 0),
                (20, 30, 1),
                (30, 50, 2),
                (50, 70, 3),
                (70, 90, 4),
                (90, 100, 5)
            ]

            for low, high, category in busy_categories:
                if low <= busy_percentage < high:
                    return category
            
            return 5  # Highest category for 90%+

        # Convert data
        converted_data = {}
        for day_data in data.get('populartimes', []):
            day_name = day_data.get('name', '')[:3].lower()
            converted_data[day_name] = [map_busy_percentage(x) for x in day_data.get('data', [])]

        # Get busy percentage
        try:
            busy_percentage = popular_times_data[current_hour] if current_hour < len(popular_times_data) else 0
        except Exception as busy_percentage_error:
            logger.warning(f"Error getting busy percentage: {busy_percentage_error}")
            busy_percentage = 0

        # Estimate wait time
        wait_time_map = [
            (0, 20, "0-5 minutes"),
            (20, 30, "5-10 minutes"),
            (30, 50, "10-20 minutes"),
            (50, 70, "20-40 minutes"),
            (70, 90, "40-60 minutes"),
            (90, 100, "60-90 minutes")
        ]

        for low, high, wait_time in wait_time_map:
            if low <= busy_percentage < high:
                return wait_time, converted_data

        return "60-90 minutes", converted_data

    except Exception as e:
        logger.error(f"Unexpected error in get_estimated_wait_time: {e}")
        return "Error retrieving wait time", {}

@app.route('/projects/api2/', methods=['POST'])
async def get_wait_time():
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    try:
        # Validate request is JSON
        if not request.is_json:
            logger.warning(f"Invalid content type for request {request_id}")
            return jsonify({"error": "Invalid content type. JSON required"}), 400

        # Parse JSON data
        data = request.get_json()
        if not data:
            logger.warning(f"Empty request body for request {request_id}")
            return jsonify({"error": "Empty request body"}), 400

        # Extract and validate place_id
        place_id = data.get('place_id')
        if not validate_place_id(place_id):
            logger.error(f"Invalid place_id in request {request_id}: {place_id}")
            return jsonify({"error": "Invalid place_id format"}), 400

        # Get estimated wait time
        wait_time, converted_data = await get_estimated_wait_time(place_id)
        
        # Log successful request
        logger.info(f"Successful wait time request {request_id} for place_id {place_id}")
        
        return jsonify({
            "request_id": request_id,
            "wait_time": wait_time, 
            "converted_data": converted_data
        })

    except asyncio.CancelledError:
        logger.warning(f"Request {request_id} was cancelled")
        return jsonify({"error": "Request was cancelled"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_wait_time for request {request_id}: {e}")
        return jsonify({"error": "Internal server error", "request_id": request_id}), 500

# Global error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Startup checks
    if not API_KEY:
        logger.critical("No API key configured. Server cannot start.")
        exit(1)
    
    try:
        # Note: Use sync run() method instead of async for Flask
        app.run(host='0.0.0.0', port=5002, debug=False)
    except Exception as startup_error:
        logger.critical(f"Failed to start server: {startup_error}")
        exit(1)