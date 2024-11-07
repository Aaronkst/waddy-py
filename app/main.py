import logging
import os
import sys
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ai import Waddy

# Ensure level is INFO or lower to see INFO messages
logging.basicConfig(level=logging.INFO)
# Create a named logger instance
logger = logging.getLogger(__name__)

# Setup
origins = [
    "*",  # TODO: set the allowed origins
]
load_dotenv()
app = FastAPI(
    port=os.getenv("PORT", 8000)
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY", "")
OPEN_AI_ASSISTANT_ID = os.getenv("OPEN_AI_ASSISTANT_ID", "")

if not len(OPEN_AI_API_KEY) or not len(OPEN_AI_ASSISTANT_ID):
    print("Please set correct environment variables. Exiting...")
    sys.exit(1)

client = Waddy(
    api_key=OPEN_AI_API_KEY,
)

# API Routes
# testing thread id: thread_DWD5dVCcK1mhgh62fpWvcXdE
@app.get('/')
def home(thread_id: str):
    try:
        return "Hello!"
    except Exception as e:
        raise HTTPException(500, str(e))

class BasicConversation(BaseModel):
    message: str

@app.post("/basic")
def basic(payload: BasicConversation):
    try:
        messages = []
        messages.append({"role": "user", "content": payload.message})

        return StreamingResponse(
            client.basic_run(
                messages=messages,
                assistant_id=OPEN_AI_ASSISTANT_ID
            ),
            media_type='text/event-stream'
        )
    except Exception as e:
        print("Error in creating thread and run from openAI:", str(e))
        raise HTTPException(500, str(e))

# testing thread id: thread_DWD5dVCcK1mhgh62fpWvcXdE
@app.get('/threads/{thread_id}')
def thread_details(thread_id: str):
    try:
        return {
            "err": 0,
            "status": "success",
            "data": client.get_thread_details(thread_id=thread_id)
        }
    except Exception as e:
        print("Error in creating thread and run from openAI:", str(e))
        raise HTTPException(500, str(e))
