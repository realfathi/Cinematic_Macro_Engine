from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from database import (
    get_industry_baseline_trends,
    get_top_10_blockbusters,
    get_profitability_split,
    get_genre_baselines,
    get_escapism_index,
    get_budget_dilemma,
    get_comedy_paradox,
    get_production_density,
    get_runtime_paradox,
    get_decade_genre_share,
    get_budget_elasticity_query,
    get_rating_kpis,
    get_financial_kpis
)

app = FastAPI(title="Cinematic Macro Engine API")

# Allow CORS for React frontend (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def df_to_dict(df):
    """Convert pandas DataFrame to a list of dicts for JSON response"""
    return df.to_dict(orient="records")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# --- Page 1: Executive Snapshot ---
@app.get("/api/industry-trends")
def api_industry_trends():
    return df_to_dict(get_industry_baseline_trends())

@app.get("/api/top-blockbusters")
def api_top_blockbusters():
    return df_to_dict(get_top_10_blockbusters())

@app.get("/api/profitability-split")
def api_profitability_split():
    return df_to_dict(get_profitability_split())

@app.get("/api/financial-kpis")
def api_financial_kpis():
    return df_to_dict(get_financial_kpis())

# --- Page 2: Macro & Crisis Impact ---
@app.get("/api/escapism-index")
def api_escapism_index():
    return df_to_dict(get_escapism_index())

@app.get("/api/budget-dilemma")
def api_budget_dilemma():
    return df_to_dict(get_budget_dilemma())

@app.get("/api/production-density")
def api_production_density():
    return df_to_dict(get_production_density())

@app.get("/api/comedy-paradox")
def api_comedy_paradox():
    return df_to_dict(get_comedy_paradox())

# --- Page 3: Structural & Runtime Trends ---
@app.get("/api/runtime-paradox")
def api_runtime_paradox():
    return df_to_dict(get_runtime_paradox())

@app.get("/api/decade-genre-share")
def api_decade_genre_share():
    return df_to_dict(get_decade_genre_share())

@app.get("/api/rating-kpis")
def api_rating_kpis():
    return df_to_dict(get_rating_kpis())

@app.get("/api/budget-elasticity")
def api_budget_elasticity():
    return df_to_dict(get_budget_elasticity_query())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
