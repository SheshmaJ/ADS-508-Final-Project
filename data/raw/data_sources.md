# Data Sources

This project uses publicly available environmental datasets.
Due to file size limitations, datasets are stored in Amazon S3 and not included directly in the repository.

### 1. NOAA Climate Data (GHCN Daily)

Source: https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily

### 2. Forest Inventory & Analysis (FIA)

Source: https://www.fia.fs.usda.gov/tools-data/

### 3. California Fire Perimeter Dataset

Source: https://data.ca.gov/dataset/california-fire-perimeters

### Storage Location

The raw datasets are stored in Amazon S3 and accessed by the data ingestion pipeline.

Example S3 structure:

s3://vegetation-risk-project/raw/fire/
s3://vegetation-risk-project/raw/forest/
s3://vegetation-risk-project/raw/weather/
