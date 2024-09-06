import asyncio
from flask import Flask, request, jsonify, render_template
from twikit import Client
import google.generativeai as genai
import requests
import os
import re
import json
import nest_asyncio
import markdown

nest_asyncio.apply()

app = Flask(__name__, template_folder=".")

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
async def analyze_tweet(url=None, tweetId=None):
    if url:
        input = re.search(r'/status/(\d+)', url)
        tweet_id = input.group(1)
    else:
        tweet_id = tweetId

    # Configure GenAI API
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

    # Prompt for the model
    prompt = (
        "Evaluate the following tweet for sensitive, political, false information, or no flagging required. "
        "Indicate if it contains any of these elements and explain why it should be flagged, or confirm that the tweet "
        "is appropriate and doesn't require flagging. First state in a sentence which flags should be raised "
        "(sensitive, political, false information, or no flagging), then give the explanation. "
        "YOU MUST RETURN IN MARKDOWN ONLY."
    )

    # Get tweet information
    tweet = await client.get_tweet_by_id(tweet_id=tweet_id)
    result2 = ""

    # Handle quoted tweets recursively
    if tweet.is_quote_status:
        quote_id = (str(tweet.quote)).split('id="')[1].split('"')[0]
        result2 = await analyze_tweet(tweetId=quote_id)

    # Analyze main tweet text
    tweet_text = tweet.text

    if tweet.media and tweet.media[0]['media_url_https']:
        media_url = tweet.media[0]['media_url_https']
        image_response = requests.get(media_url)
        image_path = "downloaded_image.jpg"

        with open(image_path, 'wb') as file:
            file.write(image_response.content)

        sample_file = genai.upload_file(path=image_path, display_name=tweet_id)
        os.remove(image_path)

        # Generate content using the tweet text and image
        response = model.generate_content(
            [sample_file, f"Tweet by {tweet.user} Tweet text here: {tweet_text}. Use the included image to {prompt}"]
        )
    else:
        # Generate content using only tweet text
        response = model.generate_content(
            f"Tweet by {tweet.user} Tweet text here: {tweet_text}. {prompt}"
        )

    # If the response contains text, return it formatted as markdown
    if response.text:
        return markdown.markdown(response.text) + result2

    return "<h2><strong>No response from Gemini API</strong></h2>"


# Define a Flask route to handle the tweet analysis
@app.route("/projects/tweet-analyzer/")
def hello():
    return render_template('test.html')

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
