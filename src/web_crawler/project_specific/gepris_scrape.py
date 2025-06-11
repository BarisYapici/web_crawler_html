import os
import time
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://gepris.dfg.de"
START_URL = BASE_URL + "/gepris/OCTOPUS?task=doKatalog&context=projekt&oldfachgebiet=22&fachgebiet=22&fachkollegium=%23&nurProjekteMitAB=false&bundesland=DEU%23&pemu=%23&zk_transferprojekt=false&teilprojekte=false&teilprojekte=true&bewilligungsStatus=&beginOfFunding=2025&gefoerdertIn=&oldGgsHunderter=0&ggsHunderter=0&einrichtungsart=-1&findButton=Finden"
SAVE_DIRECTORY = r'C:\workspace\SCAI\web_crawler\data\gepris_projects_test'
os.makedirs(SAVE_DIRECTORY, exist_ok=True)

def initialize_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 ...')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)
    return driver

def save_html(content, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def crawl_gepris_projects_all(start_url):
    driver = initialize_driver()
    driver.get(start_url)
    wait = WebDriverWait(driver, 12)
    page_count = 1

    while True:
        print(f"Processing page {page_count}...")

        # Get all project URLs as strings to avoid stale element issues
        project_links = driver.find_elements(By.CSS_SELECTOR, 'div.eintrag h2 a, div.eintrag_alternate h2 a')
        project_hrefs = []
        for link in project_links:
            href = link.get_attribute('href')
            if not href.startswith("http"):
                href = BASE_URL + href
            project_hrefs.append(href)

        for idx, href in enumerate(project_hrefs):
            driver.get(href)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
            html = driver.page_source
            url_hash = hashlib.md5(href.encode()).hexdigest()
            filename = os.path.join(SAVE_DIRECTORY, f"page{page_count}_proj{idx}_{url_hash}.html")
            save_html(html, filename)
            print(f"Saved project {idx+1} on page {page_count}")
            # Go back to the listing page
            driver.back()
            time.sleep(1)

        # Find next page link
        try:
            next_link = driver.find_element(By.CSS_SELECTOR, 'div.listennaviright a.nextactive')
            next_href = next_link.get_attribute('href')
            if not next_href.startswith("http"):
                next_href = BASE_URL + next_href
            driver.get(next_href)
            page_count += 1
            time.sleep(2)
        except Exception:
            print("No next page found. Done.")
            break

    driver.quit()

if __name__ == "__main__":
    crawl_gepris_projects_all(START_URL)