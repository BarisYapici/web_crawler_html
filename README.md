# Web Crawler Tool

This is a simple web crawler tool that uses Selenium and Requests to download HTML content from web pages. The tool starts with a list of URLs, downloads their content, and follows links found on the initial page to a specified depth.

# Features

- Headless Browsing: Utilizes Selenium's headless mode to quietly navigate and fetch web pages.
- Link Extraction: Extracts all hyperlinks from a page and visits them up to a specified depth.
- HTML Download: Downloads and saves the HTML content of each visited page.
- Unique Filenames: Ensures each downloaded page is saved uniquely using a hash of the URL.

# Prerequisites

- Python 3.x
- Google Chrome browser
- ChromeDriver (managed automatically by Selenium 4.6 and above)

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/web-crawler-tool.git
cd web-crawler-tool
```

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Ensure that your `requirements.txt` includes:

```
selenium
requests
```

# Usage

- Configure Settings: Modify the `SAVE_DIRECTORY` variable in the script to specify where downloaded HTML files should be saved.
- Run the Script: Execute the script from the command line:

```bash
python main.py
```

- Review Output: The HTML files will be saved in the specified directory, with filenames based on a hash of the URL.

# Configuration

- Starting URLs: Update the `start_urls` list in the `main` function to specify which URLs the crawler should begin with.
- Depth Control: Adjust the `max_depth` parameter in the `visit_and_save` function call to control how deep the crawler should go from the initial page (default is 1, meaning it visits links on the initial page but not deeper).

# Notes

- The tool is designed for educational purposes and should be used responsibly. Ensure compliance with websites' terms of service and robots.txt files.
- The tool leverages Selenium's automation capabilities to mimic human browsing, which can be useful for pages that require JavaScript rendering.

# License

This project is licensed under the MIT License - see the LICENSE file for details.

# Contributing

Contributions are welcome! Please submit pull requests or open issues to discuss improvements or bug fixes.