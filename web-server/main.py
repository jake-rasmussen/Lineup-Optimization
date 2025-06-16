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
    json_input: Dict[str, Optional[PlayerData]]
    method: Optional[str] = "exhaustive"
    max_iterations: Optional[int] = 1000

@app.post("/optimize-lineup")
async def optimize_lineup(request: LineupRequest):
    logging.debug(f"Received request with data: {request}")
    try:
        players_json = {
            key: {"name": value.name, "data": value.data} if value else None 
            for key, value in request.json_input.items()
        }

        result = parse_and_optimize_lineup_fast(
            players_json,
            method=request.method,
            max_iterations=request.max_iterations
        )
        return result
    except Exception as e:
        logging.error(f"Error processing lineup optimization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
