from seleniumwire import webdriver
import re

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
        # Ir al url
        driver.get("https://oficinajudicialvirtual.pjud.cl/home/index.php")
        
        # Click en boton de Consulta Causas
        consulta_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='focus']/button[contains(@onclick, 'accesoConsultaCausas')]")
            )
        )
        consulta_button.click()

        # Verificar que haya ido a la otra url
        WebDriverWait(driver, 10).until(
            EC.url_contains("indexN.php")
        )

        # Obtener el token de recaptcha
        token_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "g-recaptcha-response-rit"))
        )
        token = token_input.get_attribute("value")

        for request in driver.requests:
            if request.response and "consultaUnificada.php" in request.url:
                try:
                    body = request.response.body.decode('utf-8', errors='ignore')

                    match = re.search(r"token:\s*'([a-f0-9]{32})'", body)
                    if match:
                        token_unificado = match.group(1)
                        print("Token unificado encontrado:", token_unificado)
                except Exception as e:
                    print("Error al procesar la respuesta de la solicitud:", e)

        return token, driver.get_cookies(), token_unificado

    except Exception as e:
        print("Final URL:", driver.current_url)
        print("Page Title:", driver.title)
        raise e
    finally:
        driver.quit()

# Con selenium obtener el token y las cookies de la sesion
token, selenium_cookies, token_unificado = get_search_token_with_selenium()

# Crear una sesion de requests y usar las cookies de selenium
session = requests.Session()
for cookie in selenium_cookies:
    session.cookies.set(cookie['name'], cookie['value'])

# Headers para la consulta
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

# Payload de la consulta
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

# Hacer el post request
url = "https://oficinajudicialvirtual.pjud.cl/ADIR_871/civil/consultaRitCivil.php"
response = session.post(url, data=payload)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'lxml')
    print(f"{response.text}\n\n")
    print(token_unificado)
else:
    print(f"Request failed with status code: {response.status_code}")