import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Add CORSMiddleware to allow requests from your client (adjust origins as needed)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://lineup-optimization.vercel.app",
    "https://lineupoptimization.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import the function from your optimizer file
from lineup_optimizer import parse_and_optimize_lineup_fast

class PlayerData(BaseModel):
    name: str
    data: Optional[Dict[str, float]]

class LineupRequest(BaseModel):
    json_input: Dict[str, Any]
    method: str
    max_iterations: int

@app.post("/optimize-lineup")
async def optimize_lineup(request: LineupRequest):
    logging.debug(f"Received request with data: {request}")
    try:
        raw_input = request.json_input

        # Extract only the player entries (batting positions 1–18)
        players_json = {
            key: {
                "name": value["name"],
                "data": value["data"],
                "batting_hand": value.get("batting_hand", "RIGHT"),
            }
            for key, value in raw_input.items()
            if key.isdigit() and value is not None and "name" in value and "data" in value
        }

        # Append handedness constraints to players_json (expected by optimizer)
        players_json["max_consecutive_left"] = raw_input.get("max_consecutive_left", 0)
        players_json["max_consecutive_right"] = raw_input.get("max_consecutive_right", 0)

        result = parse_and_optimize_lineup_fast(
            json_input=players_json,
            method=request.method,
            max_iterations=request.max_iterations
        )

        return result

    except Exception as e:
        logging.error(f"Error processing lineup optimization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))