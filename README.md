# ADS-508-Final-Project
Predicting Vegetation Growth Risk for Tree Trimming Prioritization Using Machine Learning

# Project Overview
This project develops a data-driven vegetation management system that analyzes forestry, wildfire, and weather data to identify areas where vegetation growth may increase wildfire risk. The goal is to help utilities prioritize tree trimming and vegetation management to reduce wildfire risk and improve infrastructure reliability.

# Problem Statement
Vegetation growing near power lines is a major cause of wildfire risk in California. Current vegetation management relies on routine inspections and fixed trimming schedules, which are often reactive and inefficient. This project aims to use environmental and wildfire data to identify high-risk vegetation areas and support more proactive vegetation management decisions.

# Data Sources

The project integrates multiple public datasets: (refer data/raw/data_sources.md )

**Forest Inventory and Analysis (FIA)**- Tree characteristics (diameter, height, species), Terrain information (slope and aspect), Biomass measurements

**CAL FIRE Wildfire Dataset**- Historical wildfire incidents,Fire size, location, and date

**NOAA Weather Data (via Meteostat)**- Temperature,Precipitation,Wind speed,Atmospheric pressure

These datasets were downloaded from public government sources and stored in AWS S3 for analysis.

# Tools Used
**AWS Services**

Amazon S3 – Cloud storage for raw and processed datasets

AWS SageMaker Studio – Data exploration and analysis environment

**Python Libraries**

pandas – Data processing and analysis

numpy – Numerical computations

matplotlib / seaborn – Data visualization

meteostat – Weather data retrieval

boto3 – Interaction with AWS S3 storage

# Contributions to the Project this week

Built a cloud-based data pipeline using AWS S3 and SageMaker.

Integrated forest, wildfire, and weather datasets into a unified dataset.

Performed exploratory data analysis to identify factors associated with wildfire risk.


# Key Findings

**Data Quality Checks**
Datasets were checked for missing values, duplicates, and data consistency before analysis.

Some variables, particularly biomass measurements and weather variables, contained missing values that required cleaning or handling during preprocessing.

Key variables such as tree characteristics, wildfire locations, and weather conditions were largely complete and suitable for analysis.

Forest, wildfire, and weather datasets were cleaned and merged to create a unified dataset and stores in S3/processed for furthur analysis.


**EDA**

Vegetation biomass is strongly associated with tree diameter and height, meaning larger trees contribute to higher wildfire fuel loads.

Biomass variables show high correlation, suggesting that only one biomass variable may be sufficient for modeling.

Wildfire size distribution is highly right-skewed, meaning most fires are small while a few fires cause extreme damage.

Weather analysis shows low median precipitation, indicating many days with dry conditions that may increase wildfire risk.

Wildfire incidents show clear seasonal patterns, with the highest activity occurring during summer months.
