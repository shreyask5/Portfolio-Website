from flask import Flask, request, jsonify
import aiohttp
import asyncio
from datetime import datetime
import populartimes
import pytz
from aiocache import Cache
from aiocache.decorators import cached

app = Flask(__name__)

# Set up an in-memory cache (Redis can be used for production)
cache = Cache(Cache.MEMORY)

API_KEY = 'AIzaSyBKVhXDTDeuA7WDuKzektli3pqtyCDWF4A'

# Asynchronous request to fetch place details from Google Places API
async def fetch_place_details(session, place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,popular_times&key={API_KEY}"
    async with session.get(url) as response:
        return await response.json()

# Asynchronous function to get populartimes data and estimate wait time
@cached(ttl=864000)  # Cache the result for 10 days (864,000 seconds)
async def get_estimated_wait_time(place_id):
    async with aiohttp.ClientSession() as session:
        # Fetch place details asynchronously
        data = await fetch_place_details(session, place_id)

        # Fetch populartimes data (blocking call, keep it for now)
        data = populartimes.get_id(API_KEY, place_id)

        # Get current day and hour
        ist_timezone = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist_timezone)  # IST Timezone
        current_day = now.strftime('%A')  # e.g., 'Monday'
        current_hour = now.hour  # 24-hour format

        # Extract popular times for the current day
        popular_times_data = None
        for day_data in data['populartimes']:
            if day_data['name'] == current_day:
                popular_times_data = day_data['data']
                break

        if popular_times_data:
            # Function to map the busy percentage to wait time category
            def map_busy_percentage(busy_percentage):
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

            # Convert the data to the required format
            converted_data = {}
            for day_data in data['populartimes']:
                day_name = day_data['name'][:3].lower()  # Use first three letters of the day in lowercase
                converted_data[day_name] = [map_busy_percentage(x) for x in day_data['data']]

            # Get busy percentage for the current hour
            busy_percentage = popular_times_data[current_hour]

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
        else:
            return "No data available for estimated wait time", {}

@app.route('/projects/api2/', methods=['POST'])
async def get_wait_time():
    data = request.get_json()
    place_id = data.get('place_id')

    if not place_id:
        return jsonify({"error": "Missing place_id"}), 400

    try:
        # Run the async function to get the estimated wait time
        wait_time, converted_data = await get_estimated_wait_time(place_id)
        return jsonify({"wait_time": wait_time, "converted_data": converted_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
