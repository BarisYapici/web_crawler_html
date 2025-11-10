"""
CORDIS Search Functions
Core functionality for searching and finding CORDIS projects.
"""

import requests
import time
import re
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict, Optional

class CordisSearcher:
    """Handle CORDIS project search and retrieval."""
    
    def __init__(self, headless=True):
        """Initialize the searcher with optional headless mode."""
        self.headless = headless
        self.driver = None
        
    def __enter__(self):
        """Context manager entry."""
        self._initialize_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.driver:
            self.driver.quit()
            
    def _initialize_driver(self):
        """Initialize Chrome WebDriver."""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(20)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def search_projects(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search for CORDIS projects using a query string.
        
        Args:
            query: Search term (project name, acronym, or full title)
            max_results: Maximum number of results to return
            
        Returns:
            List of project dictionaries with basic info
        """
        if not self.driver:
            self._initialize_driver()
            
        results = []
        
        try:
            # Construct search URL
            search_url = f"https://cordis.europa.eu/search?q={quote_plus(query)}&p=1&num=10&srt=Relevance:decreasing"
            print(f"Searching: {search_url}")
            
            self.driver.get(search_url)
            
            # Wait for search results to load
            WebDriverWait(self.driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CLASS_NAME, "result")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='result-item']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".search-result")),
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'result')]"))
                )
            )
            
            # Try multiple selectors for search results
            result_selectors = [
                ".result",
                "[data-testid='result-item']", 
                ".search-result",
                "div[class*='result']",
                "article",
                ".project-item"
            ]
            
            result_elements = []
            for selector in result_selectors:
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if result_elements:
                    print(f"Found {len(result_elements)} results with selector: {selector}")
                    break
                    
            if not result_elements:
                # Fallback: try to find any links to project pages
                project_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/project/id/')]")
                print(f"Fallback: Found {len(project_links)} project links")
                
                for link in project_links[:max_results]:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    # Extract project ID from URL
                    match = re.search(r'/project/id/(\d+)', href)
                    if match:
                        project_id = match.group(1)
                        results.append({
                            'id': project_id,
                            'url': href,
                            'title': text or 'Unknown Title',
                            'relevance_score': 0.5  # Default score for fallback
                        })
                        
                return results[:max_results]
            
            # Parse result elements
            for i, element in enumerate(result_elements[:max_results]):
                try:
                    result = self._parse_search_result(element, i)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Error parsing result {i}: {e}")
                    continue
                    
        except TimeoutException:
            print("Search timed out - trying alternative approach")
            # Could implement API fallback here if available
            
        except Exception as e:
            print(f"Search error: {e}")
            
        return results
        
    def _parse_search_result(self, element, index: int) -> Optional[Dict]:
        """Parse a single search result element."""
        try:
            # Try to find project link
            link_element = None
            
            # Multiple ways to find the project link
            link_selectors = [
                "a[href*='/project/id/']",
                ".title a",
                ".result-title a", 
                "h3 a",
                "h2 a"
            ]
            
            for selector in link_selectors:
                try:
                    link_element = element.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
                    
            if not link_element:
                # Try xpath as fallback
                try:
                    link_element = element.find_element(By.XPATH, ".//a[contains(@href, '/project/id/')]")
                except NoSuchElementException:
                    return None
                    
            href = link_element.get_attribute('href')
            title = link_element.text.strip()
            
            # Extract project ID
            match = re.search(r'/project/id/(\d+)', href)
            if not match:
                return None
                
            project_id = match.group(1)
            
            # Skip non-main project pages (reporting, factsheet, etc.) but allow results pages
            if any(keyword in href for keyword in ['/reporting', '/factsheet']):
                return None
                
            # Normalize URL to main project page (remove language codes)
            base_url = re.sub(r'/project/id/(\d+)/[a-z]{2}$', r'/project/id/\1', href)
            
            # Try to get additional info
            description = ""
            try:
                desc_element = element.find_element(By.CSS_SELECTOR, ".description, .summary, .teaser")
                description = desc_element.text.strip()
            except NoSuchElementException:
                pass
                
            # Calculate relevance score based on position
            relevance_score = max(1.0 - (index * 0.1), 0.1)
            
            return {
                'id': project_id,
                'url': base_url,  # Use normalized URL
                'title': title,
                'description': description,
                'relevance_score': relevance_score
            }
            
        except Exception as e:
            print(f"Error parsing search result: {e}")
            return None
            
    def get_direct_xml_url(self, project_id: str) -> str:
        """
        Get direct XML download URL for a project.
        
        Args:
            project_id: CORDIS project ID
            
        Returns:
            XML download URL
        """
        return f"https://cordis.europa.eu/project/id/{project_id}?format=xml"
        
    def verify_project_exists(self, project_id: str) -> bool:
        """
        Verify if a project ID exists and is accessible.
        
        Args:
            project_id: CORDIS project ID
            
        Returns:
            True if project exists and is accessible
        """
        try:
            xml_url = self.get_direct_xml_url(project_id)
            response = requests.get(xml_url, timeout=10)
            # Check if response is XML and contains project data
            if response.status_code == 200:
                content = response.text.lower()
                return 'xml' in content and 'project' in content and project_id in content
            return False
        except Exception:
            return False

def test_search_function():
    """Test the search functionality with known projects."""
    test_queries = [
        "COMMUTE",
        "COMORBIDITY MECHANISMS UTILIZED IN HEALTHCARE",
        "101136957"  # Direct ID search
    ]
    
    print("=== Testing CORDIS Search Function ===")
    
    with CordisSearcher(headless=False) as searcher:  # Use visible browser for debugging
        for query in test_queries:
            print(f"\n--- Testing query: '{query}' ---")
            results = searcher.search_projects(query, max_results=5)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title'][:50]}...")
                print(f"     ID: {result['id']} | Score: {result['relevance_score']:.2f}")
                print(f"     URL: {result['url']}")
                
                # Verify XML access
                xml_url = searcher.get_direct_xml_url(result['id'])
                exists = searcher.verify_project_exists(result['id'])
                print(f"     XML: {xml_url} ({'✓' if exists else '✗'})")
                print()
                
            if not results:
                print("  No results found")
                
            time.sleep(2)  # Be polite to the server

if __name__ == "__main__":
    test_search_function()