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

@app.get("/api/queries")
def api_get_queries(era: str = "All"):
    import inspect
    import database
    
    results = []
    
    # Get all functions defined in database.py
    for name, func in inspect.getmembers(database, inspect.isfunction):
        if name.startswith("get_"):
            docstring = inspect.getdoc(func) or "No description available."
            source = inspect.getsource(func)
            
            # Very basic extraction: find the string between query = \"\"\" and \"\"\"
            # Since ast parsing might be complex for this specific snippet, simple string splitting works well for this pattern.
            query_str = ""
            if "query = \"\"\"" in source:
                parts = source.split("query = \"\"\"")
                if len(parts) > 1:
                    query_str = parts[1].split("\"\"\"")[0].strip()
            elif "query = f\"\"\"" in source:
                parts = source.split("query = f\"\"\"")
                if len(parts) > 1:
                    query_str = parts[1].split("\"\"\"")[0].strip()
            
            if query_str:
                results.append({
                    "name": name,
                    "description": docstring,
                    "sql": query_str
                })
    
    return results

# --- Page 1: Executive Snapshot ---
@app.get("/api/industry-trends")
def api_industry_trends(era: str = "All"):
    return df_to_dict(get_industry_baseline_trends(era))

@app.get("/api/top-blockbusters")
def api_top_blockbusters(era: str = "All"):
    return df_to_dict(get_top_10_blockbusters(era))

@app.get("/api/profitability-split")
def api_profitability_split(era: str = "All"):
    return df_to_dict(get_profitability_split(era))

@app.get("/api/financial-kpis")
def api_financial_kpis(era: str = "All"):
    return df_to_dict(get_financial_kpis(era))

# --- Page 2: Macro & Crisis Impact ---
@app.get("/api/escapism-index")
def api_escapism_index(era: str = "All"):
    return df_to_dict(get_escapism_index(era))

@app.get("/api/budget-dilemma")
def api_budget_dilemma(era: str = "All"):
    return df_to_dict(get_budget_dilemma(era))

@app.get("/api/production-density")
def api_production_density(era: str = "All"):
    return df_to_dict(get_production_density(era))

@app.get("/api/comedy-paradox")
def api_comedy_paradox(era: str = "All"):
    return df_to_dict(get_comedy_paradox(era))

# --- Page 3: Structural & Runtime Trends ---
@app.get("/api/runtime-paradox")
def api_runtime_paradox(era: str = "All"):
    return df_to_dict(get_runtime_paradox(era))

@app.get("/api/decade-genre-share")
def api_decade_genre_share(era: str = "All"):
    return df_to_dict(get_decade_genre_share(era))

@app.get("/api/rating-kpis")
def api_rating_kpis(era: str = "All"):
    return df_to_dict(get_rating_kpis(era))

@app.get("/api/budget-elasticity")
def api_budget_elasticity(era: str = "All"):
    return df_to_dict(get_budget_elasticity_query(era))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
