# Geospatial Health Demand

This repository contains materials for investigating spatial aspects of healthcare usage in the United Kingdom. It includes processing notebooks, a small Streamlit user interface and supporting utility modules.

## Project Layout

- **notebooks/**: Jupyter notebooks used for exploratory work and data preparation.
- **src/**: Placeholder for Python modules (currently empty) that will hold reusable code such as geospatial utilities or machine learning models.
- **app/**: A basic Streamlit application for interactive views.
- **data/**: Folder intended for raw and processed datasets (not included in version control).
- **tests/**: Space for future unit tests.

## Quick Start

1. Create the environment from the provided Conda file:
   ```bash
   conda env create -f environment.yml
   conda activate research_geo_env
   ```
2. Launch the Streamlit interface:
   ```bash
   streamlit run app/Home.py
   ```
3. Explore the notebooks in the `notebooks/` directory to reproduce analyses or develop new ones.

## Notes

- Source code is still under development and many modules are placeholders.
- Data files are expected to be stored in `data/raw` and `data/processed` but are not distributed with this project.

