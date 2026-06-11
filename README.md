# The Cinematic Macro-Economic Engine
### *How Wealth, Crisis, and History Shape Human Consumer Behavior & Cinema Trends (1970 - 2024)*

---

## 📌 Project Overview
The **Cinematic Macro-Economic Engine** is an end-to-end data engineering and advanced analytics platform designed to reverse-engineer human psychology through the lens of global box office trends and macroeconomic indicators. 

Instead of treating movie data as dry, isolated metrics, this project establishes a **Socio-Economic & Cultural Analytics Engine**. It integrates fragmented datasets—including historical geopolitical events, technology adoption cycles, and macro-economic factors (Inflation, Unemployment, GDP Growth)—to uncover non-obvious consumer behavioral insights and build data-driven predictive models.

---

## 🧠 Business Hypotheses & Core Analytics (The Mind-Blowing Insights)

This platform was built to scientifically test and prove/disprove four core sociological and economic anomalies that challenge standard business intuition:

---

## 🛠️ Tech Stack & Infrastructure

* **Language:** Python 3.14 (Pandas, NumPy, Requests, Scikit-Learn, Statsmodels, Seaborn, Matplotlib)
* **External APIs:** World Bank Open Data API (`wbgapi`), Open Movie Database API (`OMDb`)
* **Database / Data Warehouse:** Microsoft SQL Server (T-SQL, Window Functions, CTEs)
* **Orchestration & ETL:** Custom modular Python Ingestion & Processing Scripts (Ingestion, Cleaning, Mapping, Bulk Loading)
* **ORMs & Connectors:** SQLAlchemy, pyodbc
* **Business Intelligence / UI:** Streamlit Interactive Dashboard
* **Version Control:** Git / GitHub (Adhering to Conventional Commits standard)

---

## 📐 Data Warehouse Architecture & Schema (Star Schema)

The PostgreSQL analytical warehouse follows Ralph Kimball’s robust dimensional modeling principles, deploying a **Star Schema** designed for maximum query efficiency, performance, and clear separations of concerns.

* **fact_box_office (The Core Engine):** Stores measurable quantitative data (Budget, Revenue, Calculated ROI, IMDb Ratings, Vote Counts).
* **dim_movies:** Metadata describing the product (Movie ID, Title, Genres, Runtime).
* **dim_macroeconomics:** Yearly economic snapshots (GDP Growth Rate, Inflation Rate, Unemployment Rate).
* **dim_geopolitical_events:** Maps years to specific socio-political climates, defaulting to 'Stable Period' safely for anomaly detection.
* **dim_date:** Temporal dimension for decade-over-decade aggregations and timeline analysis.
