# Web Crawler Tool

This is a web crawler tool that allows you to download, process, and filter web pages starting from a list of URLs. The tool uses Selenium and Requests to navigate and fetch web pages, Beautiful Soup to clean and extract text content, and a keyword-based filtering system to categorize pages based on their relevance to your project.

## Features

- **Headless Browsing:** Utilizes Selenium's headless mode to quietly navigate and fetch web pages without opening a browser window.
- **Link Extraction:** Extracts all hyperlinks from a page and visits them up to a specified depth.
- **HTML Download:** Downloads and saves the HTML content of each visited page.
- **Text Extraction:** Uses Beautiful Soup to strip HTML tags and extract clean text from downloaded pages.
- **Content Filtering:** Implements keyword-based filtering to categorize pages as relevant or irrelevant based on their content.
- **Unique Filenames:** Ensures each downloaded page is saved uniquely using a hash of the URL.
- **Customizable Keywords and Thresholds:** Allows you to adjust keyword lists and relevance thresholds to fine-tune the filtering process.

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

4. **Filter Content**

   Use the `filter_keywords.py` script to classify the cleaned text files as relevant or irrelevant based on specified keywords:
    ``` 
    python filter_keywords.py
    ```
- Relevant files will be moved to a `relevant` directory.
   - Irrelevant files will be moved to an `irrelevant` directory.
   - The script will output the classification results and summary counts.

## Configuration

### Web Crawler Settings (`main.py`)

- **Starting URLs:** Update the `start_urls` list to specify which URLs the crawler should begin with.
- **Depth Control:** Adjust the `max_depth` parameter in the `visit_and_save` function call within `main.py` to control how deep the crawler should go from the initial page (default is 1, meaning it visits links on the initial page but not deeper).

### Cleaning Script Settings (`strip_html.py`)

- **Input Folder:** Set the `html_folder` variable to the directory containing the downloaded HTML files.
- **Output Folder:** Set the `output_folder` variable to where the cleaned text files will be saved.

### Filtering Script Settings (`filter_keywords.py`)

- **Input Folder:** Set the `input_folder` variable to the directory containing the cleaned text files.
- **Output Folders:** Specify `output_folder_relevant` and `output_folder_irrelevant` for where to save classified files.
- **Keyword List:** Modify the `RELEVANT_KEYWORDS` list in `filter_keywords.py` to include terms relevant to your project.

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