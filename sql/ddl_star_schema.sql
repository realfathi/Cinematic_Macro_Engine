-- 1. Create the Database
CREATE DATABASE CinematicMacroDB;
GO

USE CinematicMacroDB;
GO

-- ===================================================
-- 2. Create Movies Dimension
-- ===================================================
CREATE TABLE dim_movies (
    movie_key INT IDENTITY(1,1) PRIMARY KEY,
    movie_id INT NOT NULL UNIQUE,          -- Original TMDB/IMDb Movie ID
    title NVARCHAR(500) NOT NULL,
    genre NVARCHAR(100),
    runtime INT,
    overview NVARCHAR(MAX)
);

-- ===================================================
-- 3. Create Date Dimension
-- ===================================================
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,              -- Using the Year itself as the Key (e.g., 2008)
    release_year INT NOT NULL,
    decade NVARCHAR(50) NOT NULL
);

-- ===================================================
-- 4. Create Macroeconomics Dimension 
-- ===================================================
CREATE TABLE dim_macroeconomics (
    year INT PRIMARY KEY,                  -- Year is now the Direct Primary Key
    gdp_growth_rate REAL,
    unemployment_rate REAL,
    inflation_rate REAL
);

-- ===================================================
-- 5. Create Geopolitical Events Dimension
-- ===================================================
CREATE TABLE dim_geopolitical_events (
    event_year INT PRIMARY KEY,           -- The year itself acts as the Primary Key
    event_name NVARCHAR(500) NOT NULL,
    event_type NVARCHAR(250) NOT NULL
);

-- ===================================================
-- 6. Create Central Fact Table 
-- ===================================================
CREATE TABLE fact_box_office (
    fact_key INT IDENTITY(1,1) PRIMARY KEY,
    movie_key INT NOT NULL,
    
    -- This single key acts as the Foreign Key for Date, Macro, and Events dimensions
    date_key INT NOT NULL,                
    
    budget BIGINT,
    revenue BIGINT,
    roi REAL,
    vote_average REAL,
    vote_count INT,
    popularity REAL,
    
    -- Establish Relationships
    CONSTRAINT FK_fact_movies FOREIGN KEY (movie_key) REFERENCES dim_movies(movie_key),
    
    -- Link date_key directly to the 3 temporal dimensions simultaneously!
    CONSTRAINT FK_fact_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT FK_fact_macro FOREIGN KEY (date_key) REFERENCES dim_macroeconomics(year),
    CONSTRAINT FK_fact_events FOREIGN KEY (date_key) REFERENCES dim_geopolitical_events(event_year)
);
GO