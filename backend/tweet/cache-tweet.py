import asyncio
from flask import Flask, request, jsonify
from flask_caching import Cache
from twikit import Client
import google.generativeai as genai
import requests
import os
import re
import json
import nest_asyncio
import markdown

nest_asyncio.apply()

app = Flask(__name__)

# Configure Flask-Caching
app.config['CACHE_TYPE'] = 'SimpleCache'  # Use a simple in-memory cache
app.config['CACHE_DEFAULT_TIMEOUT'] = 2592000  # Cache timeout in seconds
cache = Cache(app)

# Global client variable to store the logged-in client instance
client = None

# Function to initialize the client and handle login
async def initialize_client():
    global client
    client = Client(language='en-US')

    # Attempt to load cookies first
    try:
        client.load_cookies('cookies.json')
        print("Successfully loaded cookies.")
    except Exception as e:
        print(f"Failed to load cookies: {e}")

    # If login with cookies fails, log in with credentials and save cookies
        logged_in = 0
        while logged_in != 30:
            try:
                await client.login(
                    auth_info_1='NumberF224',
                    auth_info_2='numberformula3@gmail.com',
                    password='number2002'
                )
                client.save_cookies('cookies.json')
                print("Logged in and saved new cookies.")
                break
            except Exception as e:
                print(f"Login failed: {e}")
                logged_in += 1

# Your tweet analysis function
async def analyze_tweet(url):
    input = re.search(r'/status/(\d+)', url)
    genai.configure(api_key="AIzaSyCLH4gSwF5iLPm21U06DzSBUdX6rTH5f1w")

    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        tools='code_execution',
    )
    
    prompt = (
        "You are tasked with evaluating tweets for potential flagging based on the following categories:"
        "Sensitive Content, Political Content, False Information, Hate Speech, Spam or Promotional Content, Harassment or Cyberbullying, Violent Content, Propaganda, Mental Health Concerns, and Fake or Manipulated Media."
        "For each tweet:"
        "Determine which flags should be raised (e.g., Sensitive, Political, False Information, or No Flagging Required)."
        "Explain why the flag(s) were raised or confirm that the tweet is appropriate and does not require flagging."
        "Output Format:"
        "Begin with a concise sentence stating the flags raised (or state \"No Flagging Required\")."
        "Follow this with a clear explanation of why the flag(s) apply or why the tweet is appropriate."
        "Example Response (Markdown):"
        "**Flags Raised**: Sensitive, Hate Speech"
        "**Explanation**: The tweet contains graphic language targeting a specific group, which can be deemed hateful and sensitive to readers. This violates content guidelines on hate speech and sensitive content."
        "If no flagging is required:"
        "**Flags Raised**: No Flagging Required"
        "**Explanation**: The tweet does not contain any inappropriate or harmful elements. It aligns with content guidelines and is appropriate for general viewing."
        "Ensure clarity, fairness, and thorough justification for every evaluation."
    )

    tweet_id = input.group(1)

    # Check if the result is cached
    cached_result = cache.get(tweet_id)
    if cached_result:
        print(f"Cache hit for tweet ID: {tweet_id}")
        return cached_result

    # Fetch and analyze the tweet
    tweet = await client.get_tweet_by_id(tweet_id=tweet_id)
    
    if tweet.is_quote_status:
        quote = (str(tweet.quote)).split('id="')[1].split('"')[0]
        new_tweet = await client.get_tweet_by_id(tweet_id=quote)
        tweet_text = new_tweet.text + " " + tweet.text
    else:
        tweet_text = tweet.text

    # Get user name
    user_id, name = None, None
    match = re.search(r'id="(\d+)"', str(tweet.user))
    if match:
        user_id = match.group(1)    
        try:
            user = await client.get_user_by_id(user_id)
            if user:
                name = user.name
        except Exception as e:
            print(f"Failed to fetch user information: {e}")

    if tweet.media and tweet.media[0]['media_url_https']:
        media_url = tweet.media[0]['media_url_https']
        image_response = requests.get(media_url)
        image_path = "downloaded_image.jpg"

        with open(image_path, 'wb') as file:
            file.write(image_response.content)

        sample_file = genai.upload_file(path=image_path, display_name=tweet_id)
        os.remove(image_path)

        response = model.generate_content(
            [sample_file, f"Verified and Tweeted By: {name} Tweet text here: {tweet_text}   Use the included image to {prompt}"]
        )
    else:
        response = model.generate_content(
            f"Verified and Tweeted By: {name} Tweet text here: {tweet_text}                {prompt}"
        )
    
    if response.text:
        result_html = markdown.markdown(response.text)
        cache.set(tweet_id, result_html)  # Cache the result
        return result_html
    
    return "<h2><strong>No response from Gemini API</strong></h2>"

# Define a Flask route to handle the tweet analysis
@app.route('/projects/api/', methods=['POST'])
def analyze_tweet_route():
    data = request.json
    url = data.get('url')
    loop = asyncio.get_event_loop()  # Get the existing event loop
    result = loop.run_until_complete(analyze_tweet(url))  # Run the async function in the existing loop
    
    return jsonify({"analysis": result})

if __name__ == '__main__':
    asyncio.run(initialize_client())
    app.run(host='0.0.0.0', port=5000, debug=True)
