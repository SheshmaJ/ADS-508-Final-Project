# Data Sources

This project uses publicly available environmental datasets obtained from government agencies and open data portals. Due to large file sizes, the datasets are not stored directly in the Git repository. Instead, they are stored in AWS S3, which acts as the project’s data lake and allows efficient access during data ingestion and analysis.


### 1. Forest Inventory & Analysis (FIA)

Source: https://www.fia.fs.usda.gov/tools-data/

**CA_TREE.csv**	249 MB	446,321	Provides tree-level information such as species, height, diameter, and biomass used to measure vegetation density.

**CA_SUBPLOT.csv**	23.2 MB	178,918	Contains subplot-level forest measurements used to link vegetation observations to specific forest plots.

**CA_TREE_REGIONAL_BIOMASS.csv**	42.3 MB	390,956	Includes biomass estimates that help measure vegetation fuel load and forest structure.

**CA_PLOT.CSV**	9.1MB	43,815	Provides location and site information for vegetation analysis


### 2. CAL FIRE Wildfire Incident Dataset 

This dataset contains historical wildfire incident records across California, including fire location (latitude and longitude), burned area, and incident dates. It is used to analyze wildfire occurrence patterns and identify fire-prone regions.

Source:
https://www.fire.ca.gov/incidents

**California_Historic_Fire_data.csv**	1.2 MB	3,300	Historical wildfire data used to identify fire-prone regions and wildfire risk patterns across California.


### 3. NOAA Climate Data (via Meteostat API)

Weather observations from NOAA weather stations were accessed using the Meteostat Python library, which provides historical climate data such as temperature, precipitation, and wind speed.

Source:
https://meteostat.net

Original NOAA data source:
https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

**NOAA_Weather_Data.csv**	38 MB	120,000+	Historical weather observations (temperature, rainfall, wind) used to analyze weather-driven vegetation growth.



# S3 structure:

s3://vegetation-risk-ml/raw/fire/

s3://vegetation-risk-ml/raw/forest/

s3://vegetation-risk-ml/raw/weather/
