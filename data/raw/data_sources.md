# Data Sources

This project uses publicly available environmental datasets obtained from government agencies and open data portals. Due to large file sizes, the datasets are not stored directly in the Git repository. Instead, they are stored in AWS S3, which acts as the project’s data lake and allows efficient access during data ingestion and analysis.


### 1. Forest Inventory & Analysis (FIA)

Source: https://www.fia.fs.usda.gov/tools-data/

### 2. CAL FIRE Wildfire Incident Dataset 

This dataset contains historical wildfire incident records across California, including fire location (latitude and longitude), burned area, and incident dates. It is used to analyze wildfire occurrence patterns and identify fire-prone regions.

Source:
https://www.fire.ca.gov/incidents

### 3. NOAA Climate Data (via Meteostat API)

Weather observations from NOAA weather stations were accessed using the Meteostat Python library, which provides historical climate data such as temperature, precipitation, and wind speed.

Source:
https://meteostat.net

Original NOAA data source:
https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

### Storage Location

The raw datasets are stored in Amazon S3 and accessed by the data ingestion pipeline.

S3 structure:

s3://vegetation-risk-ml/raw/fire/

s3://vegetation-risk-ml/raw/forest/

s3://vegetation-risk-ml/raw/weather/
