import signal
import sys
from typing import List
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from aiconsole.aic_types import StaticManual, Strategy
from aiconsole.analyse import analyse
from aiconsole.gpt.gpt_types import GPTMessage
from aiconsole.interpreter import execute

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyseHTTPRequest(BaseModel):
    messages: List[GPTMessage]
    mode: str

@app.post("/analyse")
async def post_analyse(request: AnalyseHTTPRequest):
    messages = [GPTMessage(role=message.role, content=message.content)
                for message in request.messages]
    
    mode = request.mode

    analysis = await analyse(messages, mode)
    print(analysis)

    return JSONResponse(content=analysis)

class GptHTTPRequest(BaseModel):
    messages: List[GPTMessage]
    strategy: str
    relevant_manuals: List[StaticManual]
    mode: str

@app.post("/gpt")
async def post_gpt(request: GptHTTPRequest):
    messages = [GPTMessage(role=message.role, content=message.content)
                for message in request.messages]

    async def stream():
        async for result in execute(
            strategy=Strategy(id=request.strategy, usage="dupa"),
            relevant_manuals=request.relevant_manuals,
            messages=messages,
            mode="QUALITY" if request.mode == "QUALITY" else "FAST"
        ):
            yield str(result)

    return StreamingResponse(stream(), media_type='text/event-stream')

def start_backend():
    import uvicorn
    # Start the uvicorn server
    uvicorn.run("aiconsole.app:app", host="0.0.0.0",
                port=8000, reload=True)

def start():
    """
    Launched with `poetry run start` at root level

    This function also run another server, using npm start command,
    located in the web directory. Thus, total of 2 severs will be running.
    """
    
    import subprocess
    import os

    # Function to handle signal
    def signal_handler(signal, frame):
        nonlocal process

        if signal == signal.SIGINT:  # If this is a SIGINT
            print("You pressed Ctrl+C!")
            process.send_signal(signal.SIGINT)
        elif signal == signal.SIGTERM:  # If this is a SIGTERM
            print("Received shutdown command.")
            process.send_signal(signal.SIGTERM)
        else:  # For other signals
            print(f"Unhandled signal {signal} received. Forwarding to default handler.")
            signal.signal(signal, frame)


    # Get current working directory
    cwd = os.getcwd()

    # Run "npm start" in a child process
    process = subprocess.Popen(["npm", "start"], cwd=os.path.join(cwd, "web"))

    try:
        # Start the uvicorn server
        start_backend()
    except KeyboardInterrupt: 
        # If a keyboard interrupt is received, send SIGINT to the signal handler
        signal_handler(signal.SIGINT, sys._getframe())

    # Register signal handler for SIGTERM
    signal.signal(signal.SIGTERM, signal_handler)
