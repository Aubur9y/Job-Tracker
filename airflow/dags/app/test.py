from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def test_chromedriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome"

    try:
        # Specify the ChromeDriver executable path using the Service class
        service = Service(executable_path="/home/airflow/.local/bin/chromedriver")
        
        # Initialize the WebDriver
        driver = webdriver.Chrome(
            service=service,
            options=options
        )
        
        # Navigate to a website
        driver.get("https://www.google.com")
        print(f"Page title: {driver.title}")
        
        # Close the WebDriver
        driver.quit()
        print("ChromeDriver test succeeded!")
    except Exception as e:
        print(f"ChromeDriver test failed: {e}")

if __name__ == "__main__":
    test_chromedriver()