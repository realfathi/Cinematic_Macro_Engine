import os
import pandas as pd
from sqlalchemy import create_engine, text

# ==========================================
# 1. DATABASE CONNECTION CONFIGURATION
# ==========================================
SERVER_NAME = 'Arrow'  # Change to your SQL Server instance name if needed
DATABASE_NAME = 'CinematicMacroDB'

connection_string = f"mssql+pyodbc://{SERVER_NAME}/{DATABASE_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(connection_string)

# ==========================================
# 2. LOAD DATASETS
# ==========================================
master_csv_path = os.path.join('data', 'processed', 'master_staging_movies.csv')
macro_csv_path = os.path.join('data', 'processed', 'macro_historical_dataset.csv')

if not os.path.exists(master_csv_path):
    raise FileNotFoundError(f"Missing master CSV: {master_csv_path}")
if not os.path.exists(macro_csv_path):
    raise FileNotFoundError(f"Missing macro historical CSV: {macro_csv_path}")

print("🚀 Loading datasets into memory...")
df_master = pd.read_csv(master_csv_path)
df_macro_src = pd.read_csv(macro_csv_path)

# Ensure proper data types and filter out movies with insufficient votes
df_master['imdb_votes'] = pd.to_numeric(df_master['imdb_votes'], errors='coerce').fillna(0)
df_master = df_master[df_master['imdb_votes'] >= 1000]

# Ensure proper data types
df_master['year'] = df_master['year'].fillna(0).astype(int)
df_macro_src['year'] = df_macro_src['year'].astype(int)

# ==========================================
# 3. POPULATE DIMENSIONS (Optimized with Bulk Inserts)
# ==========================================

# --- A. Populate dim_date ---
print("📦 Populating dim_date...")
valid_years = df_master[df_master['year'] > 0]['year'].unique()
dim_date_df = pd.DataFrame({'date_key': valid_years})

dim_date_df['release_year'] = dim_date_df['date_key']
dim_date_df['decade'] = (dim_date_df['release_year'] // 10 * 10).astype(str) + 's'

existing_dates = pd.read_sql("SELECT date_key FROM dim_date", engine)['date_key']
dim_date_df = dim_date_df[~dim_date_df['date_key'].isin(existing_dates)]

if not dim_date_df.empty:
    dim_date_df.to_sql('dim_date', engine, if_exists='append', index=False)

# --- B. Populate dim_macroeconomics ---
print("📦 Populating dim_macroeconomics...")
dim_macro_df = df_macro_src[['year', 'gdp_growth', 'unemployment_rate', 'inflation_rate']].rename(
    columns={'gdp_growth': 'gdp_growth_rate'}
).drop_duplicates(subset=['year'])

existing_macro = pd.read_sql("SELECT year FROM dim_macroeconomics", engine)['year']
dim_macro_df = dim_macro_df[~dim_macro_df['year'].isin(existing_macro)]

if not dim_macro_df.empty:
    dim_macro_df.to_sql('dim_macroeconomics', engine, if_exists='append', index=False)

# --- C. Populate dim_movies ---
print("📦 Populating dim_movies...")
dim_movies_df = df_master[['id', 'title', 'genres', 'runtime', 'overview']].rename(
    columns={'id': 'movie_id', 'genres': 'genre'}
).drop_duplicates(subset=['movie_id'])
dim_movies_df['overview'] = dim_movies_df['overview'].fillna('')

existing_movies = pd.read_sql("SELECT movie_id FROM dim_movies", engine)['movie_id']
dim_movies_df = dim_movies_df[~dim_movies_df['movie_id'].isin(existing_movies)]

if not dim_movies_df.empty:
    dim_movies_df.to_sql('dim_movies', engine, if_exists='append', index=False)

# --- D. Populate dim_geopolitical_events ---
print("📦 Populating dim_geopolitical_events year-by-year from source...")
events_df = df_macro_src[['year', 'event_name', 'event_type']].rename(
    columns={'year': 'event_year'}
).drop_duplicates(subset=['event_year'])

events_df['event_name'] = events_df['event_name'].fillna('Stable Period')
events_df['event_type'] = events_df['event_type'].fillna('Stable Period')

existing_events = pd.read_sql("SELECT event_year FROM dim_geopolitical_events", engine)['event_year']
events_df = events_df[~events_df['event_year'].isin(existing_events)]

if not events_df.empty:
    events_df.to_sql('dim_geopolitical_events', engine, if_exists='append', index=False)

# ==========================================
# 4. POPULATE THE MAIN FACT TABLE
# ==========================================
print("🔥 Mapping and Populating fact_box_office (The Core Engine)...")

movies_lookup = pd.read_sql("SELECT movie_key, movie_id FROM dim_movies", engine).set_index('movie_id')['movie_key'].to_dict()
fact_records = []
skipped = 0

df_master['imdb_rating'] = pd.to_numeric(df_master['imdb_rating'], errors='coerce')
C = df_master['imdb_rating'].mean()
m = 1000

for _, row in df_master.iterrows():
    m_id = int(row['id'])
    yr = int(row['year']) 
    
    if yr == 0:
        skipped += 1
        continue
        
    movie_key = movies_lookup.get(m_id)

    if movie_key is None:
        skipped += 1
        continue
    
    bgt = float(row['budget']) if pd.notna(row['budget']) else 0.0
    rev = float(row['revenue']) if pd.notna(row['revenue']) else 0.0
    calculated_roi = ((rev - bgt) / bgt) if bgt > 0 else 0.0
    
    R = 0.0 if pd.isna(row['imdb_rating']) else float(row['imdb_rating'])
    v = 0 if pd.isna(row['imdb_votes']) else int(row['imdb_votes'])
  
    pop_score = round((v / (v + m) * R) + (m / (v + m) * C), 3) if (v + m) > 0 else 0.0 
     
    fact_records.append({
        "movie_key": movie_key,
        "date_key": yr, 
        "budget": int(bgt),
        "revenue": int(rev),
        "roi": calculated_roi,
        "vote_average": R,
        "vote_count": v,
        "popularity": pop_score
    })

fact_df = pd.DataFrame(fact_records)

with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE fact_box_office"))

if not fact_df.empty:
    fact_df.to_sql('fact_box_office', con=engine, if_exists='append', index=False, chunksize=1000)

print(f"✅ Done. Inserted {len(fact_df)} fact rows. Skipped {skipped} rows.")
print("🏆 Data Warehouse ETL Pipeline is FULLY AUTOMATED & ALIVE! 🎉")