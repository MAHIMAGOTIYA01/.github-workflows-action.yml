import time
import uuid
from typing import List
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse

app = FastAPI()

# Configuration constants (Replace with your actual email)
ALLOWED_ORIGIN = "https://dash-6cftk6.example.com"
YOUR_EMAIL = "your-email@example.com" 

@app.middleware("http")
async def add_custom_headers_and_cors(request: Request, call_next):
    start_time = time.time()
    
    # 1. Handle Preflight (OPTIONS) requests manually for strict CORS control
    if request.method == "OPTIONS":
        response = Response()
        origin = request.headers.get("Origin")
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # 2. Process the actual request
    response = await call_next(request)
    
    # 3. Inject mandatory middleware headers
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    # 4. Inject CORS header for standard requests if the origin matches perfectly
    origin = request.headers.get("Origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        
    return response

@app.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        # Parse the comma-separated string into a list of integers
        num_list = [int(v.strip()) for v in values.split(",") if v.strip()]
        
        if not num_list:
            return JSONResponse(status_code=400, content={"error": "No valid numbers provided"})
        
        # Compute descriptive statistics
        count = len(num_list)
        total_sum = sum(num_list)
        minimum = min(num_list)
        maximum = max(num_list)
        mean = total_sum / count
        
        return {
            "email": YOUR_EMAIL,
            "count": count,
            "sum": total_sum,
            "min": minimum,
            "max": maximum,
            "mean": round(mean, 4)  # Safely within the ±0.01 tolerance limit
        }
        
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid integer format in values parameter"})
