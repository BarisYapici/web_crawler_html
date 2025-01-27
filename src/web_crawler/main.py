import os
import time
import random
import requests
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configure paths
SAVE_DIRECTORY = r'C:\workspace\SCAI\web_crawler\data\html_store'

# Create directory if it doesn't exist
os.makedirs(SAVE_DIRECTORY, exist_ok=True)

def initialize_driver():
    """
    Initialize the Chrome WebDriver with headless options.
    
    Returns:
        webdriver.Chrome: A Chrome WebDriver instance.
    """
    options = Options()
    options.add_argument('--headless')  # Run in headless mode for silent execution
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)  # Set a page load timeout of 15 seconds
    return driver

def fetch_links(driver, url):
    """
    Fetch all hyperlinks from a given URL.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        url (str): The URL to fetch links from.

    Returns:
        list: A list of URLs found on the page.
    """
    try:
        driver.get(url)
        
        # Wait for at least one link to appear with a timeout
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'a'))
        )

        links = driver.find_elements(By.TAG_NAME, 'a')
        urls = [link.get_attribute('href') for link in links if link.get_attribute('href')]
        return urls
    except TimeoutException:
        print(f"Page load timeout for {url}, skipping...")
        return []
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
        return []

def download_html(url, filename):
    """
    Download the HTML content of a given URL and save it to a file.

    Args:
        url (str): The URL to download.
        filename (str): The file path to save the HTML content.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Downloaded: {url} to {filename}")
        else:
            print(f"Failed to download {url}: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")

def visit_and_save(driver, url, depth=0, max_depth=1, visited=set()):
    """
    Visit a URL, download its content, and recursively visit linked pages.

    Args:
        driver (webdriver.Chrome): The WebDriver instance.
        url (str): The URL to visit.
        depth (int): Current depth of recursion.
        max_depth (int): Maximum depth to visit links.
        visited (set): A set of URLs that have been visited.
    """
    if depth > max_depth or url in visited:
        return

    visited.add(url)
    print(f"Visiting: {url}")

    # Generate a unique filename using a hash of the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    filename = os.path.join(SAVE_DIRECTORY, f"{depth}_{url_hash}.html")

    try:
        download_html(url, filename)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return

    if depth < max_depth:
        links = fetch_links(driver, url)
        for link in links:
            time.sleep(random.uniform(1, 5))  # Wait a random time between 1 to 5 seconds
            visit_and_save(driver, link, depth + 1, max_depth, visited)

def main():
    """
    Main function to initialize the crawler and start visiting URLs.
    """
    start_urls = [
        "https://www.ihi.europa.eu/projects-results/project-factsheets"
    ]
    
    driver = initialize_driver()
    try:
        for url in start_urls:
            visit_and_save(driver, url, max_depth=1)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()