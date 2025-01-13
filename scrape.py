import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_driver(browser="chrome", headless=True):
    """
    Initialize the Selenium WebDriver.
    """
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    # service = Service(r"E:\devtools\chromedriver-win64\chromedriver.exe")

    # if browser == "chrome":
    #     return webdriver.Chrome(service=service, options=options)
    # else:
    #     raise ValueError("Invalid browser")
    driver = uc.Chrome(options=options)
    return driver
    
def scrape_job_listing(driver, url, max_pages=5, keyword=None):
    """
    Scrape the job listing from the given URL.
    """
    driver.get(url)
    time.sleep(5)

    try:
        # Handle cookie banner
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "onetrust-policy-text"))
            )
            accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_button.click()
            print("Cookie banner accepted.")
        except Exception as e:
            print(f"No cookie banner found or already accepted: {e}")

    except Exception as e:
        print(f"Error handling cookie banner: {e}")

    job_listings = []
    current_page = 1

    while current_page <= max_pages:
        print(f"Scraping page {current_page}...")
        try:
            job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

            for job_card in job_cards:
                try:
                    # Extract job title
                    job_title = job_card.find_element(By.CLASS_NAME, "jobTitle").text

                    if keyword and keyword.lower() not in job_title.lower():
                        continue  # Skip jobs that don't match the keyword

                    # Extract job link
                    job_link = job_card.find_element(By.TAG_NAME, "a").get_attribute("href")

                    # Extract company name
                    try:
                        company_name = job_card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
                    except:
                        company_name = None

                    # Extract location
                    try:
                        location = job_card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text
                    except:
                        location = None

                    salary, job_type, schedule = None, None, None
                    try:
                        metadata_items = job_card.find_elements(By.CSS_SELECTOR, '[data-testid="attribute_snippet_testid"]')
                        if len(metadata_items) > 0:
                            salary = metadata_items[0].text  # First metadata item
                        if len(metadata_items) > 1:
                            job_type = metadata_items[1].text  # Second metadata item
                        if len(metadata_items) > 2:
                            schedule = metadata_items[2].text  # Third metadata item
                    except:
                        pass

                    # Append job details to the list
                    job_listings.append({
                        "job_title": job_title,
                        "job_link": job_link,
                        "company_name": company_name,
                        "location": location,
                        "salary": salary,
                        "job_type": job_type,
                        "schedule": schedule,
                    })
                except Exception as e:
                    print(f"Error while scraping a job card: {e}")
                    continue  # Move to the next job card
            
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="pagination-page-next"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Ensure visibility
                next_button.click()
                time.sleep(5)  # Wait for the next page to load
                current_page += 1
            except Exception as e:
                print(f"Next button not found or error clicking it: {e}")
                break  # Exit loop if no "Next" button is found
        
        except Exception as e:
            print(f"Error while scraping job listings: {e}")
            return []
        
    return job_listings