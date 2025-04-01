from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins, e.g., ["https://your-vercel-app.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComputeRequest(BaseModel):
    data: int

def heavy_computation(data: int):
    result = data ** 2  # Replace with your actual logic
    print(f"Computed result: {result}")

@app.post("/compute")
async def compute(request: ComputeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(heavy_computation, request.data)
    return {"message": "Computation started in the background"}

@app.get("/mock")
def mock_get():
    return {"message": "This is a mock GET response"}
