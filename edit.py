import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/run.html", "r") as f:
        return HTMLResponse(content=f.read())

# WebSocket setup
connected_clients: List[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    logging.info(f"Client connected: {websocket.client}")
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received: {data}")
            # Broadcast the message to all connected clients except the sender
            for client in connected_clients:
                if client != websocket:
                    try:
                        await client.send_text(data)
                        logging.info(f"Sent to {client.client}: {data}")
                    except Exception as e:
                        logging.error(f"Error sending to {client.client}: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        connected_clients.remove(websocket)
        logging.info(f"Client disconnected: {websocket.client}")
