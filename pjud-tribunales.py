from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import json
import pandas as pd

excel_file = "PJUD LABORAL - Estados diarios 4,3,2,1,30 OCT.xlsx" #archivo excel con la lista de tribunales
df = pd.read_excel(excel_file)

#Selenium WebDriver
driver = webdriver.Chrome()
url = "https://www.pjud.cl/tribunales/tribunales-de-primera-instancia"
driver.get(url)

json_data = []

for index, row in df.iterrows():
    corte = row["Cortes"].replace("C.A. ", "C.A ")
    tribunal = row["Tribunales 1"].upper()
    nombre_tribunal = row["Tribunales"]

    if "PITRUFQUÉN" not in tribunal: #sacarle los tildes a los tribunales, excepto pitrufquen
        tribunal = tribunal.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")

    # selector de Jurisdicción
    first_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "jurisdiccion-code")) 
    )
    select_first = Select(first_dropdown)
    select_first.select_by_visible_text(corte) # selecciona la corte

    # selector de Tribunal
    second_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "first_instance_court_id"))
    )
    select_second = Select(second_dropdown)

    try:
        select_second.select_by_visible_text(tribunal.upper()) # selecciona el tribunal
    except NoSuchElementException:
        print(f"**********(Fila {index+2}) No se encontró '{tribunal.upper()}' en '{corte}'")
        with open("no_encontrados.txt", "a", encoding="utf-8") as file:
            file.write(f"Corte: {corte}, Tribunal: {tribunal}\n")
        continue

    # obtiene el cod_tribunal
    selected_value = select_second.first_selected_option.get_attribute("value")

    print(f"(Fila {index+2}) '{nombre_tribunal}' tiene código '{selected_value}'")

    json_data.append({
        "cod_tribunal": selected_value,
        "tipo_juzgado": "111", #el tipo_juzgado da lo mismo
        "nombre_tribunal": nombre_tribunal
    })

    with open("TRIBUNALES.json", "w", encoding="utf-8") as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)

print("Scraping terminado.")

driver.quit()