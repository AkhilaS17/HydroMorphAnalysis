# HydroMorphAnalysis

This project focuses on analyzing temporal changes in water bodies using satellite imagery. It detects area changes (expansion/shrinkage) and movement patterns of water bodies using image processing techniques like NDWI and centroid shift analysis.

The workflow is implemented using Python with satellite data preprocessing, water extraction, and visualization.
##  Live Application

Access the deployed app here:

https://hydromorphanalysis-ywbtf4emsnoc62h3wlkizb.streamlit.app/

## 🛠️ Tech Stack

- Python
- Streamlit
- OpenCV
- Plotly
- NumPy
- Pandas

## Project Structure

HydroMorphAnalysis/
├── dataset/                 # Input satellite images (multi-temporal)
│   ├── 2019.tif
│   ├── 2020.tif
│   ├── ...
│
├── output/                  # Generated outputs
│   ├── ndwi_images/
│   ├── water_masks/
│   ├── graphs/
│
├── src/                     # Core implementation files
│   ├── preprocessing.py
│   ├── ndwi.py
│   ├── morphology.py
│   ├── analysis.py
│
├── main.py                  # Main execution script
├── requirements.txt         # Dependencies
├── README.md

## Features

NDWI-based water body extraction
Noise removal & mask refinement using morphology
Area-based comparison between years
Centroid shift analysis to detect directional movement
Graphical visualization of results

## 📊 Dataset Details
  Source: Sentinel-2 satellite imagery
  Format: .tif
  Bands Used:
    Green band
    Near Infrared (NIR) band
    
## Methodology (Exact Flow Used in Project)
1. Input Collection
  Multi-temporal satellite images (Sentinel-2)
2. Preprocessing
  Band selection (Green & NIR)
  Image normalization
3. NDWI Calculation
  Extract water regions
4. Thresholding
  Convert NDWI to binary water mask
5. Morphological Operations
  Remove noise
  Fill gaps
  Area Analysis
  Compare pixel area between years
6. Centroid Shift
  Track movement of water body
7. Visualization
  Output masks + graphs

## ⚙️ Getting Started
1. Clone the Repository
   git clone https://github.com/AkhilaS17/HydroMorphAnalysis.git
   cd HydroMorphAnalysis
2. Create Virtual Environment
  python -m venv venv
  venv\Scripts\activate        # Windows
  source venv/bin/activate     # Linux/Mac
3. Install Dependencies
  pip install -r requirements.txt

## Execution (Exact Steps to Run)
Step 1: Prepare Dataset
Place all satellite .tif images inside the dataset/ folder
Ensure images are from different years (e.g., 2019–2025)
All images must be of the same region
Step 2: Run Main Script
python main.py
Step 3: What Happens Internally
NDWI is computed for each image
Binary water masks are generated
Morphological cleaning is applied
Area of water bodies is calculated
Centroid positions are computed
Change detection is performed
Step 4: Output
After execution, the system generates results of,
##  Analysis Report

The project provides a detailed analysis report, including:

Water body area changes (increase/decrease)
Year-wise comparison of water extent
Quantitative results of detected changes
Centroid shift indicating movement direction

## Time-Lapse Visualization (UI)
Displays extracted water masks sequentially over time
Helps visualize how the water body evolves year by year
Shows clear patterns of expansion, shrinkage, and movement
Acts as an intuitive time-lapse animation of changes

---

