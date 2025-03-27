from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class ComputeRequest(BaseModel):
    data: int

def heavy_computation(data: int):
    # Imagine this function performs heavy computation
    result = data ** 2  # Replace with your actual logic
    print(f"Computed result: {result}")

@app.post("/compute")
async def compute(request: ComputeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(heavy_computation, request.data)
    return {"message": "Computation started in the background"}
