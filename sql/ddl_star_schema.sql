-- 1. Create the Database
CREATE DATABASE CinematicMacroDB;
GO

USE CinematicMacroDB;
GO

-- 2. Create Movies Dimension
CREATE TABLE dim_movies (
    movie_key INT IDENTITY(1,1) PRIMARY KEY,
    movie_id INT NOT NULL UNIQUE,          -- Original TMDB/IMDb Movie ID
    title NVARCHAR(500) NOT NULL,
    genre NVARCHAR(100),
    runtime INT,
);

-- 3. Create Date Dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,              -- Using the Year itself as the Key (e.g., 2008)
    release_year INT NOT NULL,
    decade NVARCHAR(50) NOT NULL
);

-- 4. Create Macroeconomics Dimension
CREATE TABLE dim_macroeconomics (
    macro_key INT IDENTITY(1,1) PRIMARY KEY,
    year INT NOT NULL UNIQUE,
    gdp_growth_rate REAL,
    unemployment_rate REAL,
    inflation_rate REAL
);

-- 5. Create Geopolitical Events Dimension (Row-by-Year Configuration)
CREATE TABLE dim_geopolitical_events (
    event_year INT PRIMARY KEY,           -- The year itself acts as the Primary Key (e.g., 1973, 2008)
    event_name NVARCHAR(500) NOT NULL,    -- Aligned with 'event_name' column from CSV
    event_type NVARCHAR(250) NOT NULL     -- Aligned with 'event_type' column from CSV
);

-- 6. Create Central Fact Table with Referential Integrity (Foreign Keys)
CREATE TABLE fact_box_office (
    fact_key INT IDENTITY(1,1) PRIMARY KEY,
    movie_key INT NOT NULL,
    date_key INT NOT NULL,
    macro_key INT NOT NULL,
    event_year_key INT,                   -- Foreign Key pointing to the exact event row of that year
    budget BIGINT,
    revenue BIGINT,
    roi REAL,
    vote_average REAL,
    vote_count INT,
    popularity REAL,
    
    -- Establish Relationships
    CONSTRAINT FK_fact_movies FOREIGN KEY (movie_key) REFERENCES dim_movies(movie_key),
    CONSTRAINT FK_fact_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT FK_fact_macro FOREIGN KEY (macro_key) REFERENCES dim_macroeconomics(macro_key),
    CONSTRAINT FK_fact_events FOREIGN KEY (event_year_key) REFERENCES dim_geopolitical_events(event_year)
);
GO