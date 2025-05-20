from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

def get_search_token_with_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    
    # Headless configuration
    options.add_argument("--headless=new")  # New headless mode
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to home page
        driver.get("https://oficinajudicialvirtual.pjud.cl/home/index.php")
        
        # Wait for page to fully load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Wait for the specific button container to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "focus"))
        )

        # Find button using parent ID and onclick attribute
        consulta_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='focus']/button[contains(@onclick, 'accesoConsultaCausas')]")
            )
        )
        consulta_button.click()

        # Verify navigation to target URL
        WebDriverWait(driver, 10).until(
            EC.url_contains("indexN.php")
        )

        # Wait for token input to be available
        token_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "g-recaptcha-response-rit"))
        )
        token = token_input.get_attribute("value")

        return token, driver.get_cookies()

    except Exception as e:
        print("Final URL:", driver.current_url)
        print("Page Title:", driver.title)
        raise e
    finally:
        driver.quit()

# Step 1: Use Selenium to get the token and cookies
token, selenium_cookies = get_search_token_with_selenium()

# Step 2: Create a requests session with Selenium's cookies
session = requests.Session()

# Add Selenium cookies to requests session
for cookie in selenium_cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# Set headers (same as your original setup)
session.headers = {
    "Accept": "*/*",
    "Accept-Language": "en,en-US;q=0.9,es;q=0.8,es-US;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "oficinajudicialvirtual.pjud.cl",
    "Origin": "https://oficinajudicialvirtual.pjud.cl",
    "Referer": "https://oficinajudicialvirtual.pjud.cl/indexN.php",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}

# Prepare payload (same as your original)
payload = {
    "g-recaptcha-response-rit": token,
    "action": "validate_captcha_rit",
    "competencia": 3,
    "conCorte": 10,
    "conTribunal": 2,
    "conTipoBusApe": 0,
    "radio-groupPenal": 1,
    "conTipoCausa": "C",
    "radio-group": 1,
    "conRolCausa": 12,
    "conEraCausa": 2020,
    "ruc1": "",
    "ruc2": "",
    "rucPen1": "",
    "rucPen2": "",
    "conCaratulado": "",
}

# Step 3: Use requests for the POST
url = "https://oficinajudicialvirtual.pjud.cl/ADIR_871/civil/consultaRitCivil.php"
response = session.post(url, data=payload)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    print(response.text)
else:
    print(f"Request failed with status code: {response.status_code}")