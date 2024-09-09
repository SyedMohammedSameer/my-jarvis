from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import subprocess
import requests
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from transformers import pipeline

# Initialize FastAPI app
app = FastAPI()

# Allow cross-origin requests for frontend
origins = [
    "http://localhost:3000",  # Next.js frontend
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
conn = sqlite3.connect('memory.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS conversations (user TEXT, assistant TEXT)''')
conn.commit()

# Set up HuggingFace model (using GPT-Neo)
gpt_model = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')

# Text-to-text conversation route
@app.post("/text-chat")
async def text_chat(request: Request):
    data = await request.json()
    user_input = data['message']

    # Use Huggingface GPT-Neo for text generation
    assistant_reply = gpt_model(user_input, max_length=150)[0]['generated_text']

    # Store conversation in the database
    c.execute("INSERT INTO conversations (user, assistant) VALUES (?, ?)", (user_input, assistant_reply))
    conn.commit()

    return {"reply": assistant_reply}

# Voice-to-voice conversation route
@app.post("/voice-chat")
async def voice_chat(request: Request):
    data = await request.json()
    voice_input_text = data['message']

    # Use GPT-Neo model to generate a response
    assistant_reply = gpt_model(voice_input_text, max_length=150)[0]['generated_text']

    # Convert the assistant reply to voice using gTTS
    tts = gTTS(assistant_reply)
    tts.save("response.mp3")

    # Play the response (if running locally)
    sound = AudioSegment.from_mp3("response.mp3")
    play(sound)

    # Store conversation in the database
    c.execute("INSERT INTO conversations (user, assistant) VALUES (?, ?)", (voice_input_text, assistant_reply))
    conn.commit()

    return {"reply": assistant_reply, "audio": "response.mp3"}

# Web search route using DuckDuckGo (free)
@app.post("/web-search")
async def web_search(request: Request):
    data = await request.json()
    query = data['query']

    search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
    search_results = requests.get(search_url).json()

    return {"results": search_results.get('RelatedTopics', [])}
