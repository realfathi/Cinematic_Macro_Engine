import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# 1. Load the hidden environment variables
load_dotenv()

# 2. Fetch the credentials safely and build engine URI
full_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
if full_uri:
    engine_uri = full_uri
else:
    db_engine = os.getenv('DB_ENGINE', 'mysql')
    user = os.getenv('DB_USER', '')
    pw = os.getenv('DB_PASS', '')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME', '')

    if db_engine.startswith('mssql'):
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        driver_enc = quote_plus(driver)
        port = port or '1433'
        engine_uri = f"mssql+pyodbc://{user}:{pw}@{host}:{port}/{db_name}?driver={driver_enc}"
    else:
        port = port or '3306'
        engine_uri = f"mysql+pymysql://{user}:{pw}@{host}:{port}/{db_name}"

engine = create_engine(engine_uri)



# ─────────────────────────────────────────────────────────────────────────────
# BASELINE KPIs — Executive Summary & Intuitive Metrics
# Basic exploratory data analysis (EDA) for the overarching industry trends.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_industry_baseline_trends():
    """
    Year-over-Year (YoY) overall industry performance.
    Shows total box office, total movies, and average ROI over time.
    """
    query = """
        SELECT 
            f.date_key                                      AS release_year,
            COUNT(f.movie_key)                              AS movies_released,
            SUM(f.budget)                                   AS total_industry_budget,
            SUM(f.revenue)                                  AS total_box_office,
            SUM(f.revenue) - SUM(f.budget)                  AS net_profit,
            ROUND(AVG(f.roi), 2)                            AS avg_roi
        FROM fact_box_office f
        WHERE f.revenue > 0 AND f.budget > 0
        GROUP BY f.date_key
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def get_top_10_blockbusters():
    """
    The All-Time Top 10 highest-grossing movies in the dataset.
    Essential for any movie dashboard.
    """
    query = """
        SELECT TOP 10
            d.title,
            f.date_key AS release_year,
            d.genre,
            f.budget,
            f.revenue,
            f.roi,
            f.vote_average
        FROM fact_box_office f
        JOIN dim_movies d ON f.movie_key = d.movie_key
        ORDER BY f.revenue DESC;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def get_profitability_split():
    """
    Categorizes movies using decimal-scale multiplier thresholds (e.g., 4.15x).
    """
    query = """
        SELECT 
            CASE 
                WHEN roi < 2.0 THEN '1. Flop (Loss)'
                WHEN roi >= 2.0 AND roi < 2.5 THEN '2. Break-Even / Marginal'
                WHEN roi >= 2.5 AND roi < 4.0 THEN '3. Profitable'
                ELSE '4. Blockbuster (>4x Budget)'
            END AS profitability_tier,
            COUNT(*) as movie_count,
            ROUND(AVG(vote_average), 2) as avg_rating
        FROM fact_box_office
        WHERE budget > 0 AND revenue > 0
        GROUP BY 
            CASE 
                WHEN roi < 2.0 THEN '1. Flop (Loss)'
                WHEN roi >= 2.0 AND roi < 2.5 THEN '2. Break-Even / Marginal'
                WHEN roi >= 2.5 AND roi < 4.0 THEN '3. Profitable'
                ELSE '4. Blockbuster (>4x Budget)'
            END
        ORDER BY profitability_tier ASC;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def get_genre_baselines():
    """
    Overall genre performance regardless of time or macro events.
    Which genre is historically the safest bet?
    """
    query = """
        SELECT 
            d.genre,
            COUNT(f.movie_key) AS total_movies,
            ROUND(AVG(CAST(f.budget AS FLOAT)), 0) AS avg_budget,
            ROUND(AVG(CAST(f.revenue AS FLOAT)), 0) AS avg_revenue,
            ROUND(AVG(f.roi), 2) AS avg_roi
        FROM fact_box_office f
        JOIN dim_movies d ON f.movie_key = d.movie_key
        WHERE f.budget > 0 AND f.revenue > 0
        GROUP BY d.genre
        HAVING COUNT(f.movie_key) > 30 -- Filter out highly niche/rare genres
        ORDER BY avg_revenue DESC;
    """
    return pd.read_sql(query, engine)

# ─────────────────────────────────────────────────────────────────────────────
# HYPOTHESIS 1 — The Box-Office Escapism Index
# Classifies years as Crisis vs. Stable and tracks genre market share over time.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_escapism_index():
    """
    Fetches genre-level revenue share split by Crisis vs. Stable economic periods.

    Returns a DataFrame with columns:
        release_year, genre, era_type, total_revenue,
        year_total_revenue, market_share_pct
    """
    query = """
        WITH yearly_genre_revenue AS (
            SELECT
                f.date_key                                              AS release_year,
                d.genre,
                -- Classify each year as Crisis or Stable based on macro indicators
                CASE
                    WHEN mac.gdp_growth_rate  < 0
                      OR mac.unemployment_rate > 8.0
                      OR ev.event_type         = 'Economic Crisis'
                    THEN 'Crisis'
                    ELSE 'Stable'
                END                                                     AS era_type,
                SUM(f.revenue)                                          AS total_revenue
            FROM fact_box_office   f
            JOIN dim_movies        d   ON f.movie_key = d.movie_key
            JOIN dim_macroeconomics mac ON f.date_key  = mac.year
            LEFT JOIN dim_geopolitical_events ev ON f.date_key = ev.event_year
            WHERE f.revenue > 0
            GROUP BY
                f.date_key,
                d.genre,
                CASE
                    WHEN mac.gdp_growth_rate  < 0
                      OR mac.unemployment_rate > 8.0
                      OR ev.event_type         = 'Economic Crisis'
                    THEN 'Crisis' ELSE 'Stable'
                END
        ),
        year_totals AS (
            SELECT
                release_year,
                era_type,
                SUM(total_revenue) AS year_total_revenue
            FROM yearly_genre_revenue
            GROUP BY release_year, era_type
        )
        SELECT
            g.release_year,
            g.genre,
            g.era_type,
            g.total_revenue,
            y.year_total_revenue,
            ROUND(
                CAST(g.total_revenue AS FLOAT) / NULLIF(y.year_total_revenue, 0) * 100,
                2
            )                                                           AS market_share_pct
        FROM yearly_genre_revenue g
        JOIN year_totals          y ON g.release_year = y.release_year
                                   AND g.era_type     = y.era_type
        ORDER BY g.release_year, g.era_type, market_share_pct DESC;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# HYPOTHESIS 2 — The Superhero Budget Dilemma
# Shows how budget distribution shifts (High / Medium / Low) during crises.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_budget_dilemma():
    """
    Bins budgets into High / Medium / Low tiers and cross-references with GDP.

    Returns a DataFrame with columns:
        release_year, budget_tier, era_type, film_count,
        avg_budget, avg_revenue, avg_roi, gdp_growth_rate
    """
    query = """
        SELECT
            f.date_key                                                  AS release_year,
            CASE
                WHEN f.budget >= 100000000 THEN 'High (>= $100M)'
                WHEN f.budget >= 20000000  THEN 'Medium ($20M–$100M)'
                ELSE                            'Low (< $20M)'
            END                                                         AS budget_tier,
            CASE
                WHEN mac.gdp_growth_rate  < 0
                  OR mac.unemployment_rate > 8.0
                  OR ev.event_type         = 'Economic Crisis'
                THEN 'Crisis'
                ELSE 'Stable'
            END                                                         AS era_type,
            COUNT(*)                                                     AS film_count,
            ROUND(AVG(CAST(f.budget  AS FLOAT)), 0)                    AS avg_budget,
            ROUND(AVG(CAST(f.revenue AS FLOAT)), 0)                    AS avg_revenue,
            ROUND(AVG(f.roi), 2)                                        AS avg_roi,
            mac.gdp_growth_rate
        FROM fact_box_office        f
        JOIN dim_macroeconomics     mac ON f.date_key = mac.year
        LEFT JOIN dim_geopolitical_events ev ON f.date_key = ev.event_year
        WHERE f.budget > 0
        GROUP BY
            f.date_key,
            CASE
                WHEN f.budget >= 100000000 THEN 'High (>= $100M)'
                WHEN f.budget >= 20000000  THEN 'Medium ($20M–$100M)'
                ELSE 'Low (< $20M)'
            END,
            CASE
                WHEN mac.gdp_growth_rate  < 0
                  OR mac.unemployment_rate > 8.0
                  OR ev.event_type         = 'Economic Crisis'
                THEN 'Crisis' ELSE 'Stable'
            END,
            mac.gdp_growth_rate
        ORDER BY release_year, budget_tier;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# HYPOTHESIS 3 — The Comedy Rating Paradox
# Revenue vs. rating gap for comedies, with a 5-year moving average.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_comedy_paradox():
    """
    Computes yearly comedy revenue, avg rating, and a 5-year moving average of
    both metrics alongside unemployment rate.

    Returns a DataFrame with columns:
        release_year, comedy_film_count, total_revenue, avg_vote_average,
        unemployment_rate, ma5_revenue, ma5_rating
    """
    query = """
        WITH comedy_yearly AS (
            SELECT
                f.date_key                              AS release_year,
                COUNT(*)                                AS comedy_film_count,
                SUM(f.revenue)                          AS total_revenue,
                ROUND(AVG(f.vote_average), 3)           AS avg_vote_average,
                mac.unemployment_rate
            FROM fact_box_office   f
            JOIN dim_movies        d   ON f.movie_key = d.movie_key
            JOIN dim_macroeconomics mac ON f.date_key  = mac.year
            WHERE LOWER(d.genre) LIKE '%comedy%'
              AND f.revenue > 0
            GROUP BY f.date_key, mac.unemployment_rate
        )
        SELECT
            release_year,
            comedy_film_count,
            total_revenue,
            avg_vote_average,
            unemployment_rate,
            -- 5-year moving average of revenue
            AVG(CAST(total_revenue AS FLOAT)) OVER (
                ORDER BY release_year
                ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
            )                                           AS ma5_revenue,
            -- 5-year moving average of rating
            AVG(avg_vote_average) OVER (
                ORDER BY release_year
                ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
            )                                           AS ma5_rating
        FROM comedy_yearly
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# HYPOTHESIS 4 — The Runtime Paradox (TikTok Effect)
# Tracks runtime trends for top-performing films vs. streaming platform launches.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_runtime_paradox():
    """
    Computes 5-year moving average of runtime for top-100 revenue films per year,
    alongside the full-year average. Flags streaming-era milestones.

    Returns a DataFrame with columns:
        release_year, avg_runtime_all, avg_runtime_top100,
        ma5_runtime_all, ma5_runtime_top100, streaming_era_flag
    """
    query = """
        WITH film_runtime_ranked AS (
            SELECT
                f.date_key                                              AS release_year,
                d.runtime,
                f.revenue,
                ROW_NUMBER() OVER (
                    PARTITION BY f.date_key
                    ORDER BY f.revenue DESC
                )                                                       AS revenue_rank
            FROM fact_box_office f
            JOIN dim_movies      d ON f.movie_key = d.movie_key
            WHERE d.runtime IS NOT NULL
              AND d.runtime > 0
        ),
        yearly_runtime AS (
            SELECT
                release_year,
                -- Average runtime for ALL films that year
                ROUND(AVG(CAST(runtime AS FLOAT)), 2)                   AS avg_runtime_all,
                -- Average runtime for TOP 100 films only
                ROUND(AVG(CAST(
                    CASE WHEN revenue_rank <= 100 THEN runtime END
                AS FLOAT)), 2)                                           AS avg_runtime_top100
            FROM film_runtime_ranked
            GROUP BY release_year
        )
        SELECT
            release_year,
            avg_runtime_all,
            avg_runtime_top100,
            -- Moving average across 5 years — smooths noise
            AVG(avg_runtime_all) OVER (
                ORDER BY release_year
                ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
            )                                                           AS ma5_runtime_all,
            AVG(avg_runtime_top100) OVER (
                ORDER BY release_year
                ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
            )                                                           AS ma5_runtime_top100,
            -- Flag streaming milestones for annotation on charts
            CASE
                WHEN release_year >= 2020 THEN 'Short-Form Era (TikTok)'
                WHEN release_year >= 2007 THEN 'Streaming Era (Netflix)'
                ELSE 'Pre-Streaming'
            END                                                         AS streaming_era_flag
        FROM yearly_runtime
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# HYPOTHESIS 5 — Sentiment & Zeitgeist Evolution
# Returns overview text + year + macro context for NLP processing in Python.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_sentiment_corpus():
    """
    Pulls movie overviews with their release year, genre, and macro context.
    Designed to feed into Python NLP (VADER / transformers / clustering).

    Returns a DataFrame with columns:
        movie_id, title, release_year, genre, overview, decade,
        gdp_growth_rate, era_type
    """
    query = """
        SELECT
            d.movie_id,
            d.title,
            f.date_key                                                  AS release_year,
            d.genre,
            d.overview,
            dt.decade,
            mac.gdp_growth_rate,
            CASE
                WHEN mac.gdp_growth_rate  < 0
                  OR mac.unemployment_rate > 8.0
                  OR ev.event_type         = 'Economic Crisis'
                THEN 'Crisis'
                ELSE 'Stable'
            END                                                         AS era_type
        FROM fact_box_office        f
        JOIN dim_movies             d   ON f.movie_key  = d.movie_key
        JOIN dim_date               dt  ON f.date_key   = dt.date_key
        JOIN dim_macroeconomics     mac ON f.date_key   = mac.year
        LEFT JOIN dim_geopolitical_events ev ON f.date_key = ev.event_year
        WHERE d.overview IS NOT NULL
          AND LEN(d.overview) > 50          -- Exclude stub overviews
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# KPI GROUP 1 — Financial KPIs
# Gross Revenue, ROI, and Inflation-Adjusted Profit.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_financial_kpis():
    """
    Returns yearly financial summary: gross revenue, average ROI,
    and Budget-to-Revenue elasticity proxy.

    Returns a DataFrame with columns:
        release_year, total_films, total_budget, total_revenue,
        avg_roi_pct, high_roi_films, gdp_growth_rate, inflation_rate
    """
    query = """
        SELECT
            f.date_key                                                  AS release_year,
            COUNT(*)                                                    AS total_films,
            SUM(f.budget)                                               AS total_budget,
            SUM(f.revenue)                                              AS total_revenue,
            -- ROI already stored in fact; average across all films for the year
            ROUND(AVG(f.roi), 2)                                        AS avg_roi_pct,
            -- Count how many films returned > 100% ROI (more than doubled budget)
            SUM(CASE WHEN f.roi > 100 THEN 1 ELSE 0 END)               AS high_roi_films,
            mac.gdp_growth_rate,
            mac.inflation_rate
        FROM fact_box_office    f
        JOIN dim_macroeconomics mac ON f.date_key = mac.year
        WHERE f.budget  > 0
          AND f.revenue > 0
        GROUP BY f.date_key, mac.gdp_growth_rate, mac.inflation_rate
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# KPI GROUP 2 — Weighted Rating & Critic vs. Audience Gap
# IMDb-style weighted rating to prevent low-vote inflation.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_rating_kpis():
    """
    Computes IMDb-style weighted rating per film and a yearly critic-gap proxy.

    Weighted Rating (WR) formula:
        WR = (v / (v + m)) * R + (m / (v + m)) * C
        Where:
            v = vote_count for this film
            m = minimum votes threshold (chosen as the 70th-percentile vote count)
            R = film's own vote_average
            C = global mean vote_average across all films

    Returns a DataFrame with columns:
        release_year, title, genre, vote_average, vote_count,
        weighted_rating, era_type, gdp_growth_rate
    """
    query = """
        WITH global_stats AS (
            SELECT
                -- CORRECTION: Added OVER () to make it a Window Function compatible with PERCENTILE_CONT
                AVG(vote_average) OVER ()                               AS global_mean,
                -- Use 70th-percentile vote count as the minimum threshold (m)
                PERCENTILE_CONT(0.70) WITHIN GROUP (ORDER BY vote_count)
                    OVER ()                                             AS min_votes_threshold
            FROM fact_box_office
            WHERE vote_count > 0
        ),
        -- We only need one row from global_stats, so collapse it
        global_single AS (
            SELECT TOP 1
                global_mean,
                min_votes_threshold
            FROM global_stats
        )
        SELECT
            f.date_key                                                  AS release_year,
            d.title,
            d.genre,
            f.vote_average,
            f.vote_count,
            -- IMDb Weighted Rating
            ROUND(
                (
                    CAST(f.vote_count AS FLOAT)
                    / (f.vote_count + g.min_votes_threshold)
                ) * f.vote_average
                +
                (
                    g.min_votes_threshold
                    / (f.vote_count + g.min_votes_threshold)
                ) * g.global_mean,
                3
            )                                                           AS weighted_rating,
            CASE
                WHEN mac.gdp_growth_rate  < 0
                  OR mac.unemployment_rate > 8.0
                  OR ev.event_type         = 'Economic Crisis'
                THEN 'Crisis'
                ELSE 'Stable'
            END                                                         AS era_type,
            mac.gdp_growth_rate
        FROM fact_box_office        f
        CROSS JOIN global_single    g
        JOIN dim_movies             d   ON f.movie_key = d.movie_key
        JOIN dim_macroeconomics     mac ON f.date_key  = mac.year
        LEFT JOIN dim_geopolitical_events ev ON f.date_key = ev.event_year
        WHERE f.vote_count > 0
        ORDER BY release_year, weighted_rating DESC;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# KPI GROUP 3 — Temporal & Structural Trends
# Decade-over-decade genre production share + production density vs. GDP.
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def get_decade_genre_share():
    """
    Tracks genre production share decade-over-decade to visualise
    the rise of Superhero films and the death of Westerns.

    Returns a DataFrame with columns:
        decade, genre, film_count, decade_total_films, genre_share_pct
    """
    query = """
        WITH genre_counts AS (
            SELECT
                dt.decade,
                d.genre,
                COUNT(*)                                                AS film_count
            FROM fact_box_office f
            JOIN dim_movies d  ON f.movie_key = d.movie_key
            JOIN dim_date   dt ON f.date_key  = dt.date_key
            GROUP BY dt.decade, d.genre
        ),
        decade_totals AS (
            SELECT
                decade,
                SUM(film_count)                                         AS decade_total_films
            FROM genre_counts
            GROUP BY decade
        )
        SELECT
            g.decade,
            g.genre,
            g.film_count,
            t.decade_total_films,
            ROUND(
                CAST(g.film_count AS FLOAT) / NULLIF(t.decade_total_films, 0) * 100,
                2
            )                                                           AS genre_share_pct
        FROM genre_counts  g
        JOIN decade_totals t ON g.decade = t.decade
        ORDER BY g.decade, genre_share_pct DESC;
    """
    return pd.read_sql(query, engine)


@st.cache_data
def get_production_density():
    """
    Compares annual film production volume against GDP growth rate.
    Answers: does output shrink, or does quality/cost increase during downturns?

    Returns a DataFrame with columns:
        release_year, total_films, avg_budget, avg_revenue,
        gdp_growth_rate, unemployment_rate, era_type
    """
    query = """
        SELECT
            f.date_key                                                  AS release_year,
            COUNT(*)                                                    AS total_films,
            ROUND(AVG(CAST(f.budget  AS FLOAT)), 0)                    AS avg_budget,
            ROUND(AVG(CAST(f.revenue AS FLOAT)), 0)                    AS avg_revenue,
            mac.gdp_growth_rate,
            mac.unemployment_rate,
            CASE
                WHEN mac.gdp_growth_rate  < 0
                  OR mac.unemployment_rate > 8.0
                  OR ev.event_type         = 'Economic Crisis'
                THEN 'Crisis'
                ELSE 'Stable'
            END                                                         AS era_type
        FROM fact_box_office        f
        JOIN dim_macroeconomics     mac ON f.date_key = mac.year
        LEFT JOIN dim_geopolitical_events ev ON f.date_key = ev.event_year
        GROUP BY
            f.date_key,
            mac.gdp_growth_rate,
            mac.unemployment_rate,
            CASE
                WHEN mac.gdp_growth_rate  < 0
                  OR mac.unemployment_rate > 8.0
                  OR ev.event_type         = 'Economic Crisis'
                THEN 'Crisis' ELSE 'Stable'
            END
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────────────────────────────────────
# BONUS — Regression Data for Budget Elasticity Analysis
# ─────────────────────────────────────────────────────────────────────────────


@st.cache_data
def get_macro_impact_data():
    """
    Backward-compatible function: fetches data for the Escapism Index
    & Budget Dilemma combined. Kept for parity with the original snippet.

    Returns a DataFrame with columns:
        release_year, budget, revenue, genres, is_crisis_year, gdp_growth_rate
    """
    query = """
        SELECT
            f.date_key                                                  AS release_year,
            f.budget,
            f.revenue,
            d.genre                                                     AS genres,
            CASE
                WHEN ev.event_type = 'Economic Crisis' THEN 1
                ELSE 0
            END                                                         AS is_crisis_year,
            mac.gdp_growth_rate
        FROM fact_box_office        f
        JOIN dim_movies             d   ON f.movie_key = d.movie_key
        JOIN dim_macroeconomics     mac ON f.date_key  = mac.year
        LEFT JOIN dim_geopolitical_events ev ON f.date_key = ev.event_year
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)


@st.cache_data
def get_budget_elasticity_query():
    """
    NEW QUERY FOR POINT 6: Aggregates yearly industry investments alongside 
    macro GDP drops to drive the budget elasticity regression scatter plot.
    """
    query = """
        SELECT 
            f.date_key AS release_year,
            SUM(CAST(f.budget AS FLOAT)) AS total_industry_investment,
            ROUND(AVG(CAST(f.budget AS FLOAT)), 0) AS avg_movie_budget,
            MAX(mac.gdp_growth_rate) AS gdp_growth_rate,
            MAX(mac.unemployment_rate) AS unemployment_rate
        FROM fact_box_office f
        JOIN dim_macroeconomics mac ON f.date_key = mac.year
        WHERE f.budget > 0
        GROUP BY f.date_key
        ORDER BY release_year;
    """
    return pd.read_sql(query, engine)