## AgriMart: A Predictive Agricultural Intelligence Framework
## By:
1. Ena Ayimey [GitHub](https://github.com/Ena753 "Ena's profile")
2. Kwame Boadi Nwanwah [GitHub](https://github.com/nwanwahkwame "Kwame's profile")
3. Olivia Matey [GitHub](https://github.com/mateyolivia-maker "Livy's repo")
4. Robert Ewonam Agbo [GitHub](https://github.com/Ing-RAKE "Ing_Rake's  repo")
5. Rebecca Eshun [GitHub](https://github.com/Eshun-Rebecca "Becks' repo")

## A capstone project

**AgriMart** is a capstone project by fellows of **Blossom Academy**, Data Scientists with certificates in **Data Science**, **Machine Learning**, and **Artificial Intelligence**. 

## Problem Statement

Farmers struggle to find buyers. If a farmer has no guaranteed market outlet, crops sit in suboptimal conditions and rot. In short, a lack of immediate marketability creates the post-harvest crisis and reduces the income for the farmer.  Further more, farmers burn agriculture waste such as maize cob, rice husk, etc., and this a major contribution to the climate change affecting us currently.

As a group, we decided to tackle this issue by building a digital marketplace that predicts produce price and connects farmers directly with buyers and industry processors. This helps buyers safely estimate how much money they will need to make purchases, while also cutting down on food waste within the supply chain. This ensures that more produced food actually reaches the market, supporting food security and promoting sustainable food systems. 

In addition to the project, we are connects farmers to waste-processing industries or buyers who, in one way or the other, will transform this waste into useful materials, like biochar fertilizers, or who would purchase them to feed animals.

## Dataset

Data was sourced from HDX and split into locations and sub-split into crops. This allowed as us to do a `Time Series` analysis on specific crops from specific locations. It spans 2006 to 2023, a significant enough period for analysis. Some crops had to be dropped entirely from the analysis. There were issues of unquantifiable conversions per price and weight, so they were ultimately dropped. Farmer data was also sourced from individuals and used as an SQL database to match with buyers.

## Folder Structure

Below is a clear project folder layout with brief descriptions and common file extensions:

```
data/
  crop_splits/         CSVs split by region & crop (.csv)
  original_dataset/    Raw source datasets (.csv)
  region_splits/       Region-based dataset splits (.csv)

models/                Trained/serialized models (.pkl)

notebooks/             Jupyter notebooks used for exploration (.ipynb)

outputs/               Generated images and artifacts (.jpg, .png)

scripts/               Reusable Python scripts invoked by main pipeline (.py)

main.py                Pipeline entry point (runs preprocessing, training, inference) (.py)
requirements.txt       Python dependency list (.txt)
README.md              Project documentation (.md)
```

# Final Insights

## Key Findings
- The dataset is suitable for time series forecasting.
- Seasonal trends exist.
- SARIMA captures both trend and seasonality.
- The model can assist:
  - Farmers
  - Agribusinesses
  - Commodity traders
  - Agricultural policy planners in Ghana

## Possible Improvements
- Add weather variables
- Include inflation data
- Add fuel and transportation costs
- Compare with Prophet and LSTM models
- Build market-specific forecasting models
