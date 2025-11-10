# CORDIS XML Collection & RAXKG Integration

<div align="center">

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.6%2B-green.svg)](https://pypi.org/project/selenium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Automated CORDIS project data collection with intelligent matching and knowledge graph integration*

</div>

## Overview

This system provides **end-to-end automation** for collecting EU research project data from CORDIS (Community Research and Development Information Service) and integrating it with the RAXKG (Research Analytics eXploration Knowledge Graph) pipeline.

## Purpose

This system automates the process of:
1. **Searching CORDIS** for projects by name/acronym/ID
2. **Downloading XML files** with project data
3. **Building knowledge graphs** using the RAXKG pipeline
4. **Importing to Neo4j** for querying and visualization
## Features

- **Headless Browsing:** Utilizes Selenium's headless mode to quietly navigate and fetch web pages without opening a browser window.
- **Link Extraction:** Extracts all hyperlinks from a page and visits them up to a specified depth.
- **HTML Download:** Downloads and saves the HTML content of each visited page.
- **Text Extraction:** Uses Beautiful Soup to strip HTML tags and extract clean text from downloaded pages.
- **Unique Filenames:** Ensures each downloaded page is saved uniquely using a hash of the URL.

## Prerequisites

- Python 3.x
- Google Chrome Browser
- ChromeDriver: Managed automatically by Selenium 4.6 and above.

### Python Packages

Ensure that your `requirements.txt` includes:

```
selenium requests beautifulsoup4
```

Additional packages used:

- `re` (Regular Expressions): Part of Python's standard library.
- `os`, `shutil`: For file and directory operations, included in the standard library.

## Installation

### Clone the Repository:
```
 git clone https://github.com/yourusername/web-crawler-tool.git cd web-crawler-tool
```
### Create a Virtual Environment (optional but recommended):

#### On Windows:
```
python -m venv venv venv\Scripts\activate
```
#### On Unix or MacOS:
``` 
python3 -m venv venv source venv/bin/activate
```
### Install the Required Python Packages:
``` 
pip install -r requirements.txt
```
## Usage

1. **Configure Settings**

   - Starting URLs: Update the `start_urls` list in the `main.py` script to specify which URLs the crawler should begin with.
   - Save Directory: Modify the `SAVE_DIRECTORY` variable in the scripts to specify where downloaded and processed files should be saved.

2. **Run the Web Crawler**

   Execute the crawler script to download HTML content from the specified starting URLs:
    ``` 
    python main.py
    ```
The HTML files will be saved in the specified directory (`html_store` by default), with filenames based on a hash of the URL.

3. **Clean HTML Files**

   Use the `strip_html.py` script to process the downloaded HTML files, removing HTML tags and extracting clean text using Beautiful Soup:
    ``` 
    python strip_html.py
    ```
The cleaned text files will be saved in a designated directory (e.g., `cleaned_text`), maintaining the same base filenames with a `.txt` extension.


## Configuration

### Web Crawler Settings (`main.py`)

- **Starting URLs:** Update the `start_urls` list to specify which URLs the crawler should begin with.
- **Depth Control:** Adjust the `max_depth` parameter in the `visit_and_save` function call within `main.py` to control how deep the crawler should go from the initial page (default is 1, meaning it visits links on the initial page but not deeper).

### Cleaning Script Settings (`strip_html.py`)

- **Input Folder:** Set the `html_folder` variable to the directory containing the downloaded HTML files.
- **Output Folder:** Set the `output_folder` variable to where the cleaned text files will be saved.

#### Thresholds:

- **Keyword Threshold:** Adjust the `threshold` parameter in the `is_relevant` function to set the minimum number of keyword matches required.
- **Minimum Length:** Adjust the `min_length` parameter in the `is_relevant` function to set the minimum number of words for a document to be considered.


## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please submit pull requests or open issues to discuss improvements or bug fixes.

## Contact

For any questions or support, please contact
 <baris.yapici@scai.fraunhofer.de>