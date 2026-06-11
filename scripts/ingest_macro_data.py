import pandas as pd
import wbgapi as wb
import os

def fetch_macro_economics():
    """
    Fetches key macroeconomic indicators from the World Bank API for the USA.
    Covers the timeline from 1970 to 2026 to align with the movie dataset.
    FIXED: Uses chronological alignment via index to prevent 'time' vs 'year' column bugs.
    """
    print("🚀 Starting macroeconomic data ingestion from World Bank API...")
    
    # Define the World Bank API indicator codes agreed upon for the project
    indicators = {
        'inflation_rate': 'FP.CPI.TOTL.ZG',        # Annual Inflation Rate (CPI %)
        'gdp_growth': 'NY.GDP.MKTP.KD.ZG',         # Annual GDP Growth (%)
        'unemployment_rate': 'SL.UEM.TOTL.ZS'      # Total Unemployment Rate (%)
    }
    
    try:
        all_data = []
        
        # Fetch each indicator separately using wb.data.DataFrame to avoid API hangs
        for indicator_name, indicator_code in indicators.items():
            print(f"  ⏳ Fetching {indicator_name}...")
            
            # Fetch data with numeric time keys to simplify year conversion
            df = wb.data.DataFrame(indicator_code, economy='USA', time=range(1970, 2027), numericTimeKeys=True)
            
            # Transpose or reset index to format rows as years, ensuring clean series
            df = df.T.reset_index()
            df.columns = ['year', indicator_name]
            
            # Ensure the year column is formatted as a clean string for unified merging
            df['year'] = df['year'].astype(str)
            all_data.append(df)
        
        # Merge all indicators together safely on the 'year' column
        df_pivot = all_data[0]
        for df in all_data[1:]:
            df_pivot = pd.merge(df_pivot, df, on='year', how='outer')
        
        # Convert clean year strings back to standard integers
        df_pivot['year'] = df_pivot['year'].astype(int)
        
        # Sort values chronologically to match baseline historical timeline
        df_pivot = df_pivot.sort_values('year').reset_index(drop=True)
        
        print("✅ Macroeconomic data ingested successfully!")
        return df_pivot
        
    except Exception as e:
        print(f"❌ Error during World Bank data ingestion: {e}")
        print("⚠️  Tip: Check your internet connection or try again later.")
        return None

def create_events_metadata():
    """
    Curates an enriched custom mapping table combining historical crises, wars, 
    and tech shifts to evaluate human behavior and cinema trends over time.
    """
    print("🧠 Building historical and tech eras metadata (Enriched Data Curation)...")
    
    # Merging economic crises, geopolitical events, pandemics, and tech shifts into one timeline (1970-2026)
    events_data = [
        # --- Economic Crises ---
        {"year": 1973, "event_name": "Oil Crisis & Stagflation", "event_type": "Economic Crisis"},
        {"year": 1979, "event_name": "Energy Crisis (Iranian Revolution Impact)", "event_type": "Economic Crisis"},
        {"year": 1987, "event_name": "Black Monday Stock Market Crash", "event_type": "Economic Crisis"},
        {"year": 2000, "event_name": "Dot-Com Bubble Burst", "event_type": "Economic Crisis"},
        {"year": 2008, "event_name": "Global Financial Crisis (Great Recession)", "event_type": "Economic Crisis"},
        {"year": 2022, "event_name": "Post-COVID Inflationary Crisis", "event_type": "Economic Crisis"},
        
        # --- Geopolitical Events & Wars ---
        {"year": 1975, "event_name": "End of Vietnam War", "event_type": "War"},
        {"year": 1990, "event_name": "Gulf War (Operation Desert Shield)", "event_type": "War"},
        {"year": 1991, "event_name": "Dissolution of the Soviet Union (End of Cold War)", "event_type": "Geopolitical"},
        {"year": 2001, "event_name": "September 11 Attacks", "event_type": "Geopolitical"},
        {"year": 2003, "event_name": "Iraq War Invasion", "event_type": "War"},
        {"year": 2022, "event_name": "Russia-Ukraine War Outbreak", "event_type": "War"},
        
        # --- Pandemics ---
        {"year": 2020, "event_name": "COVID-19 Pandemic Outbreak", "event_type": "Pandemic"},
        
        # --- Technological Eras ---
        {"year": 1982, "event_name": "Rise of Home Video (VHS Explosion)", "event_type": "Tech Era"},
        {"year": 1997, "event_name": "DVD Format Introduction & Netflix Founded", "event_type": "Tech Era"},
        {"year": 2005, "event_name": "YouTube Launch (Rise of User-Generated Video)", "event_type": "Tech Era"},
        {"year": 2007, "event_name": "Netflix Streaming Launch & First iPhone", "event_type": "Tech Era"},
        {"year": 2010, "event_name": "Smartphone & Mobile App Explosion", "event_type": "Tech Era"},
        {"year": 2018, "event_name": "TikTok Global Surge (Short-Form Video Era)", "event_type": "Tech Era"},
        {"year": 2023, "event_name": "Generative AI Boom (ChatGPT & Hollywood Strikes)", "event_type": "Tech Era"}
    ]
    
    df_events = pd.DataFrame(events_data)
    print(f"✅ Enriched metadata table created with {len(df_events)} key historical milestones!")
    return df_events

# Main execution block to merge and export external data sources
if __name__ == "__main__":
    df_macro = fetch_macro_economics()
    df_events = create_events_metadata()
    
    if df_macro is not None:
        # Merge macroeconomic data with historical events using a Left Join on 'year'
        df_merged_external = pd.merge(df_macro, df_events, on='year', how='left')
        
        # 1. Fallback for 1970-1990 Unemployment (BLS Data)
        print("🧠 Injecting official US Bureau of Labor Statistics (BLS) data for 1970-1990 gaps...")
        bls_unemployment_fallback = {
            1970: 4.9, 1971: 5.9, 1972: 5.6, 1973: 4.9, 1974: 5.6,
            1975: 8.5, 1976: 7.7, 1977: 7.1, 1978: 6.1, 1979: 5.8,
            1980: 7.1, 1981: 7.6, 1982: 9.7, 1983: 9.6, 1984: 7.5,
            1985: 7.2, 1986: 7.0, 1987: 6.2, 1988: 5.5, 1989: 5.3,
            1990: 5.6
        }
        for year, rate in bls_unemployment_fallback.items():
            mask = df_merged_external['year'] == year
            df_merged_external.loc[mask, 'unemployment_rate'] = df_merged_external.loc[mask, 'unemployment_rate'].fillna(rate)
        
        # Pre-fill event labels momentarily so we can filter 'Stable Period' accurately
        df_merged_external['event_name'] = df_merged_external['event_name'].fillna('Stable Period')
        df_merged_external['event_type'] = df_merged_external['event_type'].fillna('Stable Period')

        # ---------------------------------------------------------------------
        # 🔥 THE EXACT FIX: Calculate Benchmark from Last 5 Stable Periods for 2025 Only
        # ---------------------------------------------------------------------
        print("📊 Dynamically calculating 2025 baseline from last 5 Stable Periods...")
        
        # Filter for stable years strictly before 2025 that have valid numerical data
        stable_years_df = df_merged_external[
            (df_merged_external['event_name'] == 'Stable Period') & 
            (df_merged_external['year'] < 2025) &
            (df_merged_external['inflation_rate'].notna()) &
            (df_merged_external['gdp_growth'].notna()) &
            (df_merged_external['unemployment_rate'].notna())
        ].sort_values('year', ascending=False)
        
        # Extract the last 5 historical stable records
        last_5_stable = stable_years_df.head(5)
        print(f"📋 Benchmark years used for calculation: {last_5_stable['year'].tolist()}")
        
        # Calculate historical averages
        avg_inflation = round(last_5_stable['inflation_rate'].mean(), 14)
        avg_gdp = round(last_5_stable['gdp_growth'].mean(), 14)
        avg_unemployment = round(last_5_stable['unemployment_rate'].mean(), 14)
        
        print(f"🎯 Calculated Benchmarks -> Inflation: {avg_inflation}%, GDP Growth: {avg_gdp}%, Unemployment: {avg_unemployment}%")
        
        # ---------------------------------------------------------------------
        # Direct Overwrite for 2025 ONLY 
        # ---------------------------------------------------------------------
        print("🚀 Applying dynamic benchmarks to 2025 data points exclusively...")
        df_merged_external.loc[df_merged_external['year'] == 2025, 'inflation_rate'] = avg_inflation
        df_merged_external.loc[df_merged_external['year'] == 2025, 'gdp_growth'] = avg_gdp
        df_merged_external.loc[df_merged_external['year'] == 2025, 'unemployment_rate'] = avg_unemployment
        
        # ---------------------------------------------------------------------
        # Save Results
        # ---------------------------------------------------------------------
        os.makedirs('data/processed', exist_ok=True)
        os.makedirs('data/raw', exist_ok=True)
        
        df_merged_external.to_csv('data/processed/macro_historical_dataset.csv', index=False)
        df_merged_external.to_csv('data/raw/macro_historical_dataset.csv', index=False)
        
        print("\n🎉 Phase 0 completed dynamically! 2025 is fully populated.")
        print("💾 File saved at: `data/processed/macro_historical_dataset.csv`")
        print("\n📝 Verification preview for the final years:")
        print(df_merged_external.tail(5))
    else:
        print("⚠️  Skipping merge since macroeconomic data fetch failed.")