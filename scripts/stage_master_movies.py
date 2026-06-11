import pandas as pd
import numpy as np
import re
import os

def clean_imdb_id(val):
    """
    Strips any whitespace, quotes, and the 'tt' prefix FROM IMDb RAW TSV FILES ONLY, 
    then converts safely to a clean integer.
    """
    if pd.isna(val):
        return None
    val_str = str(val).strip().replace('"', '').replace("'", "")
    numbers = re.findall(r'\d+', val_str)
    return int(numbers[0]) if numbers else None

def build_master_staging_dataset():
    print("🎬 Starting Master Movie Dataset Integration Pipeline...")
    
    # -------------------------------------------------------------------------
    # Configuration: Explicit File Paths for your TSV deployment
    # -------------------------------------------------------------------------
    tmdb_path = 'data/processed/tmdb_processed_movies.csv'
    imdb_basics_path = 'data/raw/IMDb Complete Dataset Collection (2025)/title.basics.tsv'
    imdb_ratings_path = 'data/raw/IMDb Complete Dataset Collection (2025)/title.ratings.tsv'
    output_path = 'data/processed/master_staging_movies.csv'
    
    # -------------------------------------------------------------------------
    # Step 1: Load and Filter IMDb Basics TSV
    # -------------------------------------------------------------------------
    print("⏳ Loading and filtering IMDb Basics TSV...")
    # Official IMDb TSV files use '\t' as delimiter and '\\N' for missing values
    imdb_basics = pd.read_csv(
        imdb_basics_path, 
        sep='\t', 
        na_values='\\N', 
        low_memory=False, 
        quoting=3,
        on_bad_lines='skip'
    )
    
    # Filter strictly for features classified as a movie
    imdb_basics['titleType'] = imdb_basics['titleType'].astype(str).str.strip()
    imdb_basics = imdb_basics[imdb_basics['titleType'] == 'movie']
    
    # Standardize IMDb ID (tconst) by removing 'tt' to get clean integer keys
    imdb_basics['imdb_id_cleaned'] = imdb_basics['tconst'].apply(clean_imdb_id)
    imdb_basics = imdb_basics.dropna(subset=['imdb_id_cleaned'])
    imdb_basics['imdb_id_cleaned'] = imdb_basics['imdb_id_cleaned'].astype(int)
    
    imdb_basics = imdb_basics[['imdb_id_cleaned', 'runtimeMinutes']]
    
    # -------------------------------------------------------------------------
    # Step 2: Load and Clean IMDb Ratings TSV
    # -------------------------------------------------------------------------
    print("⏳ Loading and parsing IMDb Ratings TSV...")
    imdb_ratings = pd.read_csv(
        imdb_ratings_path, 
        sep='\t', 
        na_values='\\N', 
        quoting=3,
        on_bad_lines='skip'
    )
    
    # Convert 'tconst' to uniform integer key
    imdb_ratings['imdb_id_cleaned'] = imdb_ratings['tconst'].apply(clean_imdb_id)
    imdb_ratings = imdb_ratings.dropna(subset=['imdb_id_cleaned'])
    imdb_ratings['imdb_id_cleaned'] = imdb_ratings['imdb_id_cleaned'].astype(int)
    
    imdb_ratings = imdb_ratings[['imdb_id_cleaned', 'averageRating', 'numVotes']]
    
    # -------------------------------------------------------------------------
    # Step 3: Merge IMDb Baselines (Basics + Ratings)
    # -------------------------------------------------------------------------
    print("🔄 Integrating IMDb Tables...")
    imdb_master = pd.merge(imdb_basics, imdb_ratings, on='imdb_id_cleaned', how='inner')
    
    # -------------------------------------------------------------------------
    # Step 4: Load Cleaned TMDB Dataset (Direct Column Use)
    # -------------------------------------------------------------------------
    print(f"⏳ Loading pre-processed TMDB dataset from {tmdb_path}...")
    try:
        df_tmdb = pd.read_csv(tmdb_path)
    except FileNotFoundError:
        print(f"❌ Error: {tmdb_path} not found. Run your previous cleaner script first.")
        return
        
    # Enforce strict uniform type mapping for the baseline join key
    df_tmdb = df_tmdb.dropna(subset=['imdb_id_cleaned'])
    df_tmdb['imdb_id_cleaned'] = df_tmdb['imdb_id_cleaned'].astype(int)
    
    # -------------------------------------------------------------------------
    # Step 5: Master Left Join
    # -------------------------------------------------------------------------
    print("🚀 Executing Master Staging Join (TMDB Left Join IMDb)...")
    df_final = pd.merge(df_tmdb, imdb_master, on='imdb_id_cleaned', how='left')
    
    # -------------------------------------------------------------------------
    # Step 6: Defensive Imputation & Casting Clean Int64 Metrics
    # -------------------------------------------------------------------------
    print("🧠 Performing Data Imputation & Type Enforcements...")
    
    # Safe numerical conversion of the incoming runtime attribute from IMDb
    df_final['runtimeMinutes'] = pd.to_numeric(df_final['runtimeMinutes'], errors='coerce')
    df_final['runtime'] = df_final['runtime'].fillna(df_final['runtimeMinutes'])
    df_final.drop(columns=['runtimeMinutes'], inplace=True, errors='ignore')
    
    # Cast basic structural values to direct integer fields
    df_final['id'] = df_final['id'].astype(int)
    df_final['imdb_id_cleaned'] = df_final['imdb_id_cleaned'].astype(int)
    df_final['year'] = df_final['year'].astype(int)
    
    # SUCCESS CRITERIA: Cast financial values to clean integer formats (Removes e+08)
    df_final['budget'] = df_final['budget'].fillna(0).round().astype('int64')
    df_final['revenue'] = df_final['revenue'].fillna(0).round().astype('int64')
    df_final['runtime'] = df_final['runtime'].fillna(120).round().astype(int)
    
    # Map database schema standard column definitions
    df_final.rename(columns={
        'vote_average': 'tmdb_rating',
        'vote_count': 'tmdb_votes',
        'averageRating': 'imdb_rating',
        'numVotes': 'imdb_votes'
    }, inplace=True)
    
    # Drop obscure database rows containing zero meaningful crowd tracking data
    df_final = df_final[(df_final['imdb_votes'] >= 10) | (df_final['imdb_votes'].isna())]
    
    # Write out the structural master dataset gold staging file
    os.makedirs('data/processed', exist_ok=True)
    df_final.to_csv(output_path, index=False)
    
    print(f"\n🎉 Master Staging Integration Complete!")
    print(f"💾 Final Unified Dataset Saved At: {output_path}")
    print(f"📊 Total Production-Ready Rows: {len(df_final)}")
    print("\n📝 Corrected Data Sample Preview:")
    print(df_final[['title', 'year', 'budget', 'revenue', 'imdb_rating', 'imdb_votes']].head())

if __name__ == "__main__":
    build_master_staging_dataset()