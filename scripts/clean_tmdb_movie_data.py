import pandas as pd
import numpy as np
import json
import re

def clean_imdb_id(val):
    """
    Standardizes IMDb ID to a clean integer format.
    Extracts only numeric digits (e.g., 'tt0111161' -> 111161).
    """
    if pd.isna(val):
        return None
    numbers = re.findall(r'\d+', str(val))
    return int(numbers[0]) if numbers else None

def parse_genres(genres_val):
    """
    Robust genre parser supporting both Kaggle formats:
    1. Legacy JSON string format: '[{"name": "Action"}, {"name": "Comedy"}]'
    2. Modern TMDB plain text format: 'Action, Comedy' or 'Action|Comedy'
    Ensures no empty lists are generated if valid data exists.
    """
    if pd.isna(genres_val):
        return "Unknown"
    
    genres_str = str(genres_val).strip()
    
    # Format 1: If it looks like a JSON array, parse it structurally
    if genres_str.startswith('[') and genres_str.endswith(']'):
        try:
            # Standardize quotes for valid JSON formatting
            cleaned_json = genres_str.replace("'", '"')
            genres_list = json.loads(cleaned_json)
            extracted = [item['name'] for item in genres_list if 'name' in item]
            if extracted:
                return ", ".join(extracted)
        except Exception:
            pass  # Fall back to string parsing if JSON parsing fails
            
    # Format 2: Standard plain text string (e.g., 'Action|Comedy' or 'Action, Comedy')
    # Replace pipe separators with a standardized comma space
    cleaned_str = genres_str.replace('|', ', ')
    
    # Clean up any accidental double spaces or trailing commas
    cleaned_str = ", ".join([g.strip() for g in cleaned_str.split(',') if g.strip()])
    
    return cleaned_str if cleaned_str else "Unknown"

def strip_quotes(title):
    """
    Removes leading and trailing quotes from movie titles if they exist.
    Handles standard double quotes, single quotes, and typographic smart quotes.
    """
    if pd.isna(title):
        return title
    title_str = str(title).strip()
    if title_str.startswith(('"', "'")) and title_str.endswith(('"', "'")):
        return title_str[1:-1].strip()
    return title_str

def clean_and_filter_movies(input_path, output_path):
    print("🎬 Starting Cinematic Data Cleaning & Filtering Phase...")
    
    # Load raw dataset directly from data/raw/
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"❌ Error: Could not find the source file at {input_path}. Please verify your paths.")
        return
        
    initial_rows = len(df)
    print(f"📊 Initial dataset record count: {initial_rows}")
    
    # --------------------------------------------------------------------------
    # 🔒 Applying the 6 Core Data Cleaning Constraints
    # --------------------------------------------------------------------------
    
    # [Constraint 3] Remove rows where IMDb ID is NULL
    if 'imdb_id' in df.columns:
        df['imdb_id_cleaned'] = df['imdb_id'].apply(clean_imdb_id)
        df = df.dropna(subset=['imdb_id_cleaned'])
        df['imdb_id_cleaned'] = df['imdb_id_cleaned'].astype(int)
        print(f"🔹 Step 1 (Condition 3): Removed rows with NULL IMDb IDs. Count: {len(df)}")
    else:
        print("❌ Error: 'imdb_id' column is completely missing from the input file!")
        return

    # [Constraint 1] Remove movies where runtime is <= 0 or missing
    df = df.dropna(subset=['runtime'])
    df = df[df['runtime'] > 0]
    print(f"🔹 Step 2 (Condition 1): Filtered out invalid runtimes (<= 0 or NaN). Count: {len(df)}")
    
    # [Constraint 2] Remove rows where budget or revenue is NULL or zero
    df = df.dropna(subset=['budget', 'revenue'])
    df = df[(df['budget'] > 0) & (df['revenue'] > 0)]
    print(f"🔹 Step 3 (Condition 2): Removed records with 0 or NULL Budget/Revenue. Count: {len(df)}")
    
    # [Constraint 6] Remove extreme financial outliers greater than 4 Billion
    df = df[(df['budget'] <= 4_000_000_000) & (df['revenue'] <= 4_000_000_000)]
    print(f"🔹 Step 4 (Condition 6): Filtered out financial outliers (> 4 Billion). Count: {len(df)}")
    
    # [Constraint 4] Remove rows where vote count = 0 or vote average = 0
    df = df[(df['vote_count'] > 0) & (df['vote_average'] > 0)]
    print(f"🔹 Step 5 (Condition 4): Dropped unrated movies (Vote Count/Avg = 0). Count: {len(df)}")
    
    # [Constraint 5] Remove leading/trailing quotation marks from movie titles
    df['title'] = df['title'].apply(strip_quotes)
    print("🔹 Step 6 (Condition 5): Stripped surrounding quotes from movie titles successfully.")
    
    # --------------------------------------------------------------------------
    # 🎯 Additional Engineering Optimizations for the Data Warehouse
    # --------------------------------------------------------------------------
    
    # Synchronize timeline constraints (1970 - 2024)
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # Extract year, remove temporal null records, and enforce strict integer types
    df['year'] = df['release_date'].dt.year
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int) 
    
    # Scope data to our project baseline boundary
    df = df[(df['year'] >= 1970) & (df['year'] <= 2024)]
    print(f"🔹 Project Baseline: Filtered timeline limit (1970-2024). Current Count: {len(df)}")
    
    # Process Genres without losing fields or returning empty values
    if 'genres' in df.columns:
        df['genres'] = df['genres'].apply(parse_genres)
        print("🔹 System Processing: Restructured movie genres to a clean comma-separated format.")
    
    # Standardizing core columns to align with PostgreSQL Star Schema Warehouse requirements
    final_features = [
        'id', 'imdb_id_cleaned', 'title', 'year', 'release_date', 
        'budget', 'revenue', 'runtime', 'vote_average', 'vote_count', 
        'overview', 'genres'
    ]
    
    # Dynamic column assignment check to prevent KeyErrors
    final_features = [col for col in final_features if col in df.columns]
    df_final = df[final_features]
    
    # Export clean structured data into data/processed/ folder
    df_final.to_csv(output_path, index=False)
    print(f"\n🎉 Data Cleaning Phase Complete! Total dropped anomalies: {initial_rows - len(df_final)}")
    print(f"💾 Cleaned warehouse production dataset saved at: {output_path}")

if __name__ == "__main__":
    # Standardizing script paths: Read from absolute raw data, write to processed output
    clean_and_filter_movies(
        input_path='data/raw/TMDB_movie_dataset_v11.csv', 
        output_path='data/processed/tmdb_processed_movies.csv'
    )