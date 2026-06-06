## AgriMart: A Predictive Agricultural Intelligence Framework
## By:
1. Ena Ayimey [GitHub](https://github.com/Ena753 "Ena's profile")
2. Kwame Boadi Nwanwah [GitHub](https://github.com/nwanwahkwame "Kwame's profile")
3. Olivia Matey [GitHub](https://github.com/mateyolivia-maker "Livy's repo")
4. Robert Ewonam Agbo [GitHub](https://github.com/Ing-RAKE "Ing_Rake's repo")
5. Rebecca Eshun [GitHub](https://github.com/Eshun-Rebecca "Becks' repo")

## A capstone project

**AgriMart** is a capstone project built by fellows of **Blossom Academy** to bridge farmers, buyers, and market intelligence using data science and time series forecasting.

## Problem Statement

Farmers struggle to find buyers. When crops do not reach a market outlet quickly, they sit in suboptimal conditions and often rot. This post-harvest crisis reduces farmer income and contributes to waste.

This project tackles that challenge by building a digital marketplace that:
- connects farmers directly with buyers,
- forecasts crop price trends,
- helps buyers estimate purchase costs,
- and supports sustainable supply chains.

It also targets waste-processing industries that can convert agricultural byproducts into useful materials such as biochar fertilizers.

## Dataset

Data was sourced from the Humanitarian Data Exchange (HDX) and split into regional and crop-specific datasets. The records span 2006 to 2023 and support time series modeling on location-specific agricultural prices.

## Project structure

```
.env                   Environment variables for secure database credentials
app/                   Placeholder for future frontend or Streamlit UI code
data/
  crop_splits/         CSV files split by region and crop
  original_dataset/    Raw dataset sources
  region_splits/       CSV dataset splits by region
models/                Serialized or trained model artifacts
notebooks/             Jupyter notebooks for data exploration and analysis
outputs/               Generated visualization assets and export files
scripts/               Reusable pipeline modules for data processing and forecasting
__init__.py            Python package initializer
main.py                Pipeline entry point that runs the processing and forecasting flow
requirements.txt       Python dependency list
runtime.txt            Python runtime version for deployment
README.md              Project documentation
```

## How to set up

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the main pipeline:

```bash
python main.py
```

## Notes

- `main.py` runs the core pipeline using modules in `scripts/`.
- `scripts/` contains the data processing steps for region splitting, crop splitting, batch processing, SQL ingestion, and forecasting.
- `runtime.txt` specifies Python `3.13.12`.
- `app/` is currently a reserved location for future user interface code.
- `requirements.txt` includes packages required for the core pipeline and optional interactive tooling.

## Current workspace contents

The repository contains the following active folders and files:
- `data/` with split datasets and original sources
- `models/best_model.pkl`
- `notebooks/` for analysis
- `outputs/` with generated charts
- `scripts/` with pipeline modules
- `main.py` as the orchestrator

## Final insights

- The repository is structured as a data science pipeline with clear preprocessing and forecasting modules.
- It supports MySQL ingestion via SQLAlchemy and environment variables through `.env`.
- The codebase is ready for future frontend integration in `app/`.
