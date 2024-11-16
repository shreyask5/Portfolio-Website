import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from twikit import Client
import google.generativeai as genai
import requests
import os
import re
import json
import nest_asyncio
import markdown
from fastapi.templating import Jinja2Templates
import uvicorn

nest_asyncio.apply()

app = FastAPI()
templates = Jinja2Templates(directory=".")

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
        model_name="gemini-1.5-flash-latest",
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

    # Prompt for the model
    prompt = (
        "evalute the tweet"
    )

    # Get tweet information
    tweet = await client.get_tweet_by_id(tweet_id=tweet_id)
    result2 = ""

    # Handle quoted tweets recursively
    if tweet.is_quote_status:
        quote_id = (str(tweet.quote)).split('id=\"')[1].split('\"')[0]
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
            [sample_file, f"Tweet text here: {tweet_text}. Use the included image to {prompt}"]
        )
    else:
        # Generate content using only tweet text
        response = model.generate_content(
            f"Tweet text here: {tweet_text}. {prompt}"
        )

    # If the response contains text, return it formatted as markdown
    if response.text:
        return markdown.markdown(response.text) + result2

    return "<h2><strong>No response from Gemini API</strong></h2>"

# Define a route to render the HTML page
@app.get("/projects/tweet-analyzer/", response_class=HTMLResponse)
def hello(request: Request):
    return templates.TemplateResponse('test.html', {"request": request})

# Define a route to handle the tweet analysis
@app.post('/projects/api/')
async def analyze_tweet_route(request: Request):
    data = await request.json()
    url = data.get('url')
    result = await analyze_tweet(url)
    return JSONResponse(content={"analysis": result})

if __name__ == '__main__':
    asyncio.run(initialize_client())
    uvicorn.run(app, host="0.0.0.0", port=5000)
