"""
CORDIS Research Script
This script helps us understand how CORDIS search and XML download work.
"""

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def initialize_driver():
    """Initialize Chrome WebDriver with headless options."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)
    return driver

def test_cordis_search_patterns():
    """Test different CORDIS search URL patterns and approaches."""
    base_search_url = "https://cordis.europa.eu/search"
    
    # Test different search query formats
    test_queries = [
        "COMMUTE",
        "COMORBIDITY MECHANISMS UTILIZED IN HEALTHCARE", 
        '"COMMUTE"',  # exact match
        '"COMORBIDITY MECHANISMS UTILIZED IN HEALTHCARE"'
    ]
    
    print("Testing CORDIS search patterns...")
    for query in test_queries:
        search_url = f"{base_search_url}?q={query}"
        print(f"\nTesting: {search_url}")
        
        try:
            response = requests.get(search_url, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✓ URL accessible")
            else:
                print("✗ URL failed")
        except Exception as e:
            print(f"✗ Error: {e}")

def explore_project_page_structure(project_id="101136957"):
    """Explore the structure of a CORDIS project page to find XML download."""
    driver = initialize_driver()
    
    try:
        url = f"https://cordis.europa.eu/project/id/{project_id}"
        print(f"\nExploring project page: {url}")
        
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Look for download section and XML links
        print("\nSearching for download options...")
        
        # Check for download links containing "XML"
        xml_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'XML') or contains(@href, 'xml')]")
        print(f"Found {len(xml_links)} potential XML links:")
        for link in xml_links:
            href = link.get_attribute('href')
            text = link.text.strip()
            print(f"  - Text: '{text}' | URL: {href}")
        
        # Check for download buttons or sections
        download_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Download') or contains(text(), 'download')]")
        print(f"\nFound {len(download_elements)} download-related elements:")
        for elem in download_elements[:5]:  # Limit output
            tag = elem.tag_name
            text = elem.text.strip()
            print(f"  - Tag: {tag} | Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Look for specific download section
        try:
            download_section = driver.find_element(By.XPATH, "//h2[contains(text(), 'Download')]")
            print(f"\n✓ Found download section: {download_section.text}")
            
            # Get parent container to find download options
            parent = download_section.find_element(By.XPATH, "./..")
            download_options = parent.find_elements(By.TAG_NAME, "a")
            print(f"Download options in section:")
            for option in download_options:
                href = option.get_attribute('href')
                text = option.text.strip()
                print(f"  - '{text}' -> {href}")
                
        except Exception as e:
            print(f"No standard download section found: {e}")
            
    except Exception as e:
        print(f"Error exploring page: {e}")
    finally:
        driver.quit()

def test_xml_download_direct():
    """Test direct XML download URL patterns."""
    project_id = "101136957"
    
    # Common XML export URL patterns to test
    potential_xml_urls = [
        f"https://cordis.europa.eu/project/id/{project_id}/export/xml",
        f"https://cordis.europa.eu/project/{project_id}/xml", 
        f"https://cordis.europa.eu/export/project/{project_id}/xml",
        f"https://cordis.europa.eu/api/project/{project_id}/xml",
        f"https://cordis.europa.eu/download/project/{project_id}/xml"
    ]
    
    print(f"\nTesting potential XML URLs for project {project_id}...")
    for url in potential_xml_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"  {url} -> Status: {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"    ✓ Success! Content-Type: {content_type}")
                if 'xml' in content_type.lower():
                    print(f"    ✓ XML content confirmed")
                    # Save sample
                    with open(f"sample_project_{project_id}.xml", 'w', encoding='utf-8') as f:
                        f.write(response.text[:1000])  # Save first 1000 chars
                    print(f"    ✓ Sample saved")
        except Exception as e:
            print(f"  {url} -> Error: {e}")

def main():
    """Run all research functions."""
    print("=== CORDIS Research Script ===")
    
    # Test 1: Search patterns
    test_cordis_search_patterns()
    
    # Test 2: Project page structure  
    explore_project_page_structure()
    
    # Test 3: XML download URLs
    test_xml_download_direct()
    
    print("\n=== Research complete ===")

if __name__ == "__main__":
    main()