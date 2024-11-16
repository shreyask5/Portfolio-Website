import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from twikit import Client
import google.generativeai as genai
import requests
import os
import re
import markdown
from fastapi.templating import Jinja2Templates

# Global client and model variables
client = None
model = None

# Function to initialize the client and handle login
async def initialize_client():
    global client, model

    # Initialize the Twikit client
    client = Client(language='en-US')

    # Attempt to load cookies first
    try:
        client.load_cookies('cookies.json')
        print("Successfully loaded cookies.")
    except Exception as e:
        print(f"Failed to load cookies: {e}")
        logged_in_attempts = 0
        while logged_in_attempts < 30:  # Retry up to 30 times
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
                logged_in_attempts += 1

    # Configure GenAI API
    genai.configure(api_key="AIzaSyBKVhXDTDeuA7WDuKzektli3pqtyCDWF4A")

    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-8b-001",
        generation_config=generation_config,
        tools='code_execution',
        system_instruction=[
            "You are tasked with evaluating tweets for potential flagging based on the following categories:",
            "Sensitive Content, Political Content, False Information, Hate Speech, Spam or Promotional Content, Harassment or Cyberbullying, Violent Content, Propaganda, Mental Health Concerns, and Fake or Manipulated Media.",
            "For each tweet:",
            "Determine which flags should be raised (e.g., Sensitive, Political, False Information, or No Flagging Required).",
            "Explain why the flag(s) were raised or confirm that the tweet is appropriate and does not require flagging.",
            "Output Format:",
            "Begin with a concise sentence stating the flags raised (or state \"No Flagging Required\").",
            "Follow this with a clear explanation of why the flag(s) apply or why the tweet is appropriate.",
            "Example Response (Markdown):",
            "**Flags Raised**: Sensitive, Hate Speech",
            "**Explanation**: The tweet contains graphic language targeting a specific group, which can be deemed hateful and sensitive to readers. This violates content guidelines on hate speech and sensitive content.",
            "If no flagging is required:",
            "**Flags Raised**: No Flagging Required",
            "**Explanation**: The tweet does not contain any inappropriate or harmful elements. It aligns with content guidelines and is appropriate for general viewing.",
            "Ensure clarity, fairness, and thorough justification for every evaluation."
        ],
    )

# Function to analyze a tweet
async def analyze_tweet(url=None, tweetId=1831356844214042634):
    if url:
        match = re.search(r'/status/(\d+)', url)
        if match:
            tweet_id = match.group(1)
        else:
            raise ValueError("Invalid tweet URL")
    else:
        tweet_id = tweetId

    # Get tweet information
    tweet = await client.get_tweet_by_id(tweet_id=tweet_id)
    if not tweet:
        return "<h2><strong>Tweet not found</strong></h2>"

    result2 = ""
    print("Hello World")

    # Get user name
    user_id,name = None,None
    match = re.search(r'id="(\d+)"', str(tweet.user))
    if match:
        user_id = match.group(1)    
        try:
            user = await client.get_user_by_id(user_id)
            if user:
                name = user.name
        except Exception as e:
            print(f"Failed to fetch user information: {e}")

    # Handle quoted tweets recursively
    if tweet.is_quote_status:
        quote_id = re.search(r'id=\"(\d+)\"', str(tweet.quote)).group(1)
        if quote_id:
            result2 = await analyze_tweet(tweetId=quote_id)

    # Analyze main tweet text
    tweet_text = tweet.text

    # Check for attached media
    if tweet.media and 'media_url_https' in tweet.media[0]:
        media_url = tweet.media[0]['media_url_https']
        image_response = requests.get(media_url)
        image_path = "downloaded_image.jpg"

        with open(image_path, 'wb') as file:
            file.write(image_response.content)

        # Upload the media file to GenAI
        sample_file = genai.upload_file(path=image_path, display_name=str(tweet_id))
        os.remove(image_path)

        # Generate content using the tweet text and image
        response = model.generate_content(
            [sample_file, f"Tweet text here: {tweet_text}. Use the included image to evaluate."]
        )
    else:
        # Generate content using only tweet text
        response = model.generate_content(
            f"Tweet text here: {tweet_text}. Evaluate the content."
        )

    # If the response contains text, return it formatted as markdown
    if response.text:
        return markdown.markdown(response.text) + result2

    return "<h2><strong>No response from Gemini API</strong></h2>"

# Run initialization and analyze tweet
async def main():
    await initialize_client()
    result = await analyze_tweet()
    print(result)

asyncio.run(main())
