# bc-wildfire-prediction

This repository is dedicated to predicting wildfires in the British Columbia region using satellite imagery data. The primary goal is to leverage machine learning techniques to analyze and process satellite imagery for accurate wildfire detection.

## Directory Structure

- `sat_log_file/` - Contains functions and scripts for satellite image processing.
- `shapefiles/` - QGIS files for geographic region selection.

## Satellite Image Processing

There are two main approaches to processing satellite images contained within this repository:

### Specific Function Notebooks

- `download_sentinel2.ipynb`: Download Sentinel-2 images and split into uniform square tiles including various bands and mask files.
- `file_extraction_sentinel2.ipynb`, `file_extraction_sentinel.ipynb`: Organize the file paths of the satellite tiles and the fire occurrence data into CSV format.
- `initial_data_generation.ipynb`: Combine satellite images with fire information, adding an `if_fire` column to denote fire events.
- `image_process.ipynb`, `organize_download_images.py`, `save_processed_image.ipynb`: Compute necessary indices for model training from the bands, numerically transform the results, and store them as PNG files for future processing.

### Integrated Notebook

- `earth_platform_download.ipynb`: Consolidates the aforementioned processing steps into one comprehensive notebook.

## Model Training Notebooks

The notebooks within the `notebooks_models/` folder are designed for training the machine learning models. Each model is tailored to predict wildfire occurrences using the processed satellite data.

## Usage

To utilize this repository:

1. Begin with the `download_sentinel2.ipynb` notebook to download and preprocess satellite imagery.
2. Employ `file_extraction_sentinel*.ipynb` notebooks to structure the satellite tile information and fire data into CSV files.
3. Use `initial_data_generation.ipynb` to merge satellite data with fire incidents.
4. Execute `image_process.ipynb`, `organize_download_images.py`, and `save_processed_image.ipynb` for feature extraction and preparation for model training.
5. Alternatively, run `earth_platform_download.ipynb` for an end-to-end data processing workflow.
6. Navigate to the `notebooks_models/` directory to train the respective machine learning models.

Ensure that all necessary dependencies are installed and the QGIS shapefiles are correctly set up within the `shapefiles/` directory before running the notebooks.

