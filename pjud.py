import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

url = "https://www.pjud.cl/ajax/Courts/getDailyStatements"

with open("TRIBUNALES.json", "r", encoding="utf-8") as file: #lee el archivo TRIBUNALES.json generado por pjud-tribunales.py
    tribunales = json.load(file)

fechas = ["04-10-2024", "03-10-2024", "02-10-2024", "01-10-2024", "30-09-2024"]

for tribunal in tribunales:
    data = []
    print(f"*Procesando datos de {tribunal['nombre_tribunal']}...")
    for fecha in fechas:

        payload = {
            "cod_tribunal": tribunal["cod_tribunal"],
            "tipo_juzgado": tribunal["tipo_juzgado"],
            "nombre_tribunal": tribunal["nombre_tribunal"],
            "date": fecha
        }

        # Making the POST request
        response = requests.post(url, data=payload)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        table_laboral = soup.find("table", id="data-table-estado-diario-laboral")
        table = soup.find("table", id="data-table-estado-diario") #cuando hay una unica tabla en el tribunal

        if table_laboral:
            print(f"  - Fecha: {fecha} - OK")
            # Extract table headers
            headers = [header.text.strip() for header in table_laboral.find_all("th")]

            # Extract table rows
            for row in table_laboral.find_all("tr")[1:]:  # Skip header row
                columns = [col.text.strip() for col in row.find_all("td")]
                data.append(columns + [tribunal["nombre_tribunal"], fecha])

        elif table:
            print(f"  - Fecha: {fecha} - OK (data-table-estado-diario)")
            # Extract table headers
            headers = [header.text.strip() for header in table.find_all("th")]

            # Extract table rows
            for row in table.find_all("tr")[1:]:  # Skip header row
                columns = [col.text.strip() for col in row.find_all("td")]
                data.append(columns + [tribunal["nombre_tribunal"], fecha])
        else:
            print(f"  - Fecha: {fecha} - no hay datos")
    
    # Convert the list to a DataFrame
    if data:
        headers.extend(["TRIBUNAL", "Fecha"])
        df = pd.DataFrame(data, columns=headers)

        # Save the DataFrame to an Excel file named after nombre_tribunal
        file_name = f"{tribunal['nombre_tribunal'].replace(' ', '_')}.xlsx"
        df.to_excel(file_name, index=False)
        print(f"Estados diarios guardados en '{file_name}'")
    else:
        print(f"No hay estados diarios para {tribunal['nombre_tribunal']}.")