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
    # Basic format check for Google API Key
    api_key_pattern = r'^AIza[A-Za-z0-9_-]{35}$'
    return re.match(api_key_pattern, api_key) is not None

# Secure API Key handling
try:
    API_KEY = 'AIzaSyAdPSNAoMbA-InKeHDH1G-w_ctNmVaadRg'
    if not validate_api_key(API_KEY):
        raise ValueError("Invalid Google API Key format")
except Exception as key_error:
    logger.critical(f"API Key configuration error: {key_error}")
    API_KEY = None

# Validate Place ID
def validate_place_id(place_id):
    # Place ID typically starts with 'ChI' and contains alphanumeric characters
    place_id_pattern = r'^ChI[A-Za-z0-9_-]+$'
    return (
        place_id is not None 
        and isinstance(place_id, str) 
        and re.match(place_id_pattern, place_id) is not None
    )

# Asynchronous request to fetch place details from Google Places API
async def fetch_place_details(session, place_id):
    # Generate a unique request ID for tracking
    request_id = str(uuid.uuid4())
    
    # Validate inputs
    if not validate_place_id(place_id):
        logger.error(f"Invalid place_id: {place_id} for request {request_id}")
        raise ValueError(f"Invalid place ID format for request {request_id}")
    
    if not API_KEY:
        logger.error(f"API Key not configured for request {request_id}")
        raise RuntimeError("Google Places API key is not configured")
    
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,popular_times&key={API_KEY}"
    
    try:
        async with session.get(url, timeout=10) as response:
            # Check for HTTP errors
            if response.status != 200:
                logger.error(f"HTTP error {response.status} for request {request_id}")
                raise aiohttp.HttpProcessingError(f"HTTP error {response.status}")
            
            # Parse JSON response with error handling
            try:
                data = await response.json()
            except ValueError as json_error:
                logger.error(f"JSON parsing error for request {request_id}: {json_error}")
                raise

            # Check for API-level errors
            if data.get('status') != 'OK':
                error_message = data.get('error_message', 'Unknown API error')
                logger.error(f"Google Places API error for request {request_id}: {error_message}")
                raise RuntimeError(f"API Error: {error_message}")
            
            return data
    except (aiohttp.ClientError, asyncio.TimeoutError) as network_error:
        logger.error(f"Network error for request {request_id}: {network_error}")
        raise

# Asynchronous function to get populartimes data and estimate wait time
@cached(ttl=864000)  # Cache the result for 10 days (864,000 seconds)
async def get_estimated_wait_time(place_id):
    # Validate place ID again for safety
    if not validate_place_id(place_id):
        logger.error(f"Invalid place_id in get_estimated_wait_time: {place_id}")
        raise ValueError("Invalid place ID")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Fetch place details asynchronously
            data = await fetch_place_details(session, place_id)

            # Fetch populartimes data with error handling
            try:
                data = populartimes.get_id(API_KEY, place_id)
            except Exception as populartimes_error:
                logger.error(f"Populartimes data fetch error: {populartimes_error}")
                raise RuntimeError("Unable to fetch populartimes data")

            # Validate data structure
            if not data or 'populartimes' not in data:
                logger.warning(f"No populartimes data available for place_id: {place_id}")
                return "No data available for estimated wait time", {}

            # Get current day and hour with robust timezone handling
            try:
                ist_timezone = pytz.timezone('Asia/Kolkata')
                now = datetime.now(ist_timezone)  # IST Timezone
                current_day = now.strftime('%A')  # e.g., 'Monday'
                current_hour = now.hour  # 24-hour format
            except Exception as timezone_error:
                logger.error(f"Timezone error: {timezone_error}")
                current_day = None
                current_hour = None

            # Extract popular times for the current day
            popular_times_data = None
            for day_data in data.get('populartimes', []):
                if day_data.get('name') == current_day:
                    popular_times_data = day_data.get('data', [])
                    break

            if not popular_times_data or current_hour is None:
                logger.warning(f"No popular times data for {current_day} or invalid hour")
                return "No data available for estimated wait time", {}

            # Robust function to map the busy percentage to wait time category
            def map_busy_percentage(busy_percentage):
                try:
                    busy_percentage = float(busy_percentage)
                except (TypeError, ValueError):
                    logger.warning(f"Invalid busy percentage: {busy_percentage}")
                    return 0

                if 0 <= busy_percentage < 20:
                    return 0
                elif 20 <= busy_percentage < 30:
                    return 1
                elif 30 <= busy_percentage < 50:
                    return 2
                elif 50 <= busy_percentage < 70:
                    return 3
                elif 70 <= busy_percentage < 90:
                    return 4
                else:
                    return 5

            # Robust data conversion with error handling
            try:
                converted_data = {}
                for day_data in data.get('populartimes', []):
                    day_name = day_data.get('name', '')[:3].lower()  # Use first three letters of the day in lowercase
                    converted_data[day_name] = [map_busy_percentage(x) for x in day_data.get('data', [])]
            except Exception as conversion_error:
                logger.error(f"Data conversion error: {conversion_error}")
                converted_data = {}

            # Get busy percentage for the current hour with safety checks
            try:
                busy_percentage = popular_times_data[current_hour] if current_hour < len(popular_times_data) else 0
            except Exception as busy_percentage_error:
                logger.warning(f"Error getting busy percentage: {busy_percentage_error}")
                busy_percentage = 0

            # Estimate wait time based on busy percentage
            if busy_percentage < 20:
                wait_time = "0-5 minutes"
            elif busy_percentage < 30:
                wait_time = "5-10 minutes"
            elif 30 <= busy_percentage < 50:
                wait_time = "10-20 minutes"
            elif busy_percentage < 70:
                wait_time = "20-40 minutes"
            elif busy_percentage < 90:
                wait_time = "40-60 minutes"
            else:  # For 90% and above
                wait_time = "60-90 minutes"

            return wait_time, converted_data

    except Exception as e:
        logger.error(f"Unexpected error in get_estimated_wait_time: {e}")
        return "Error retrieving wait time", {}

@app.route('/projects/api2/', methods=['POST'])
async def get_wait_time():
    # Generate a unique request ID for tracking
    request_id = str(uuid.uuid4())
    
    try:
        # Validate request content type
        if not request.is_json:
            logger.warning(f"Invalid content type for request {request_id}")
            return jsonify({"error": "Invalid content type. JSON required"}), 400

        # Parse and validate JSON data
        data = request.get_json()
        if not data:
            logger.warning(f"Empty request body for request {request_id}")
            return jsonify({"error": "Empty request body"}), 400

        # Extract place_id with validation
        place_id = data.get('place_id')
        if not validate_place_id(place_id):
            logger.error(f"Invalid place_id in request {request_id}: {place_id}")
            return jsonify({"error": "Invalid place_id format"}), 400

        # Run the async function to get the estimated wait time
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

# Add global error handlers for Flask
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {error}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Additional startup checks
    if not API_KEY:
        logger.critical("No API key configured. Server cannot start.")
        exit(1)
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False)
    except Exception as startup_error:
        logger.critical(f"Failed to start server: {startup_error}")
        exit(1)