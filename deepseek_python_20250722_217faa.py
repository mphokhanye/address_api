from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import csv
from pathlib import Path

app = FastAPI(title="Address Lookup & Validation API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load sample data (replace with your full dataset)
DATA_PATH = Path("sample_data/postalcodes.csv")

def load_data():
    with open(DATA_PATH) as f:
        return [row for row in csv.DictReader(f)]

# 1. Autocomplete Endpoint
@app.get("/autocomplete")
async def autocomplete(query: str = Query(..., min_length=2)):
    """Suggest suburb/area matches based on partial input"""
    data = load_data()
    results = [
        {
            "suburb": item["suburb"],
            "area": item["area"],
            "street_code": int(item["street_code"]),
            "box_code": item["box_code"]
        }
        for item in data
        if query.lower() in item["suburb"].lower()
    ]
    return {"results": results}

# 2. Validation Endpoint
@app.get("/validate")
async def validate(
    suburb: str = Query(..., min_length=2),
    area: str = Query(..., min_length=2)
):
    """Validate suburb/area combination"""
    data = load_data()
    
    # Check for exact match
    exact_match = next(
        (item for item in data 
         if item["suburb"].lower() == suburb.lower()
         and item["area"].lower() == area.lower()),
        None
    )
    
    if exact_match:
        return {
            "valid": True,
            "details": {
                "suburb": exact_match["suburb"],
                "area": exact_match["area"],
                "street_code": int(exact_match["street_code"]),
                "box_code": exact_match["box_code"]
            }
        }
    
    # Check for partial matches
    suggestions = [
        {
            "suburb": item["suburb"],
            "area": item["area"]
        }
        for item in data
        if suburb.lower() in item["suburb"].lower()
        or area.lower() in item["area"].lower()
    ]
    
    return {
        "valid": False,
        "message": "No exact match" + (", but here are similar results." if suggestions else " found."),
        "suggestions": suggestions if suggestions else []
    }