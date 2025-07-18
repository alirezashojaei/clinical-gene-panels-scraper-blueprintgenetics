# Clinical Gene Panels Scraper - Blueprint Genetics

A Python-based web scraper for extracting structured data from Blueprint Genetics clinical gene panel listings. This tool collects comprehensive information including panel names, associated genes, specialties, and detailed panel content for bioinformatics research and clinical applications.

## Features

- **Comprehensive Data Extraction**: Scrapes panel names, categories, links, and detailed gene information
- **Concurrent Processing**: Efficiently processes multiple panels simultaneously (batch processing)
- **Database Management**: Automatic CSV database creation and updates
- **Resume Capability**: Continues from where it left off, skipping already processed panels
- **Progress Tracking**: Real-time progress bar with detailed status updates
- **Error Handling**: Robust error handling with detailed logging

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd clinical-gene-panels-scraper-blueprintgenetics
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python main.py
```

### Custom Database Path
```bash
python main.py --database-path /path/to/custom/database.csv
```

### Command Line Options
- `--database-path`: Specify custom path for the database CSV file (default: `data/blueprint_panels_database.csv`)
- `--help`: Show help message


## How It Works

1. **Panel Discovery**: Scrapes the main Blueprint Genetics website to find all available test panels
2. **Database Update**: Updates the local CSV database with new panels
3. **Content Extraction**: Concurrently scrapes detailed gene information for each panel
4. **Progress Tracking**: Shows real-time progress with success/error indicators
5. **Resume Support**: Automatically skips panels that have already been processed


