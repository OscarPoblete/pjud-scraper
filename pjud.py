import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.pjud.cl/ajax/Courts/getDailyStatements"

# List of tribunal data
tribunales = [
    #C.A. de Rancagua
    {"cod_tribunal": "3473301", "tipo_juzgado": "8", "nombre_tribunal": "Juzgado De Letras Y Garantia De Peumo"},
    {"cod_tribunal": "3553301", "tipo_juzgado": "8", "nombre_tribunal": "1º Juzgado De Letras De San Fernando"},
    {"cod_tribunal": "3553302", "tipo_juzgado": "8", "nombre_tribunal": "2º Juzgado De Letras De San Fernando"},
    {"cod_tribunal": "3603301", "tipo_juzgado": "8", "nombre_tribunal": "1º Juzgado De Letras De Santa Cruz"},
    {"cod_tribunal": "3703301", "tipo_juzgado": "8", "nombre_tribunal": "Juzgado De Letras Y Garantia De Pichilemu"},
    {"cod_tribunal": "3723301", "tipo_juzgado": "8", "nombre_tribunal": "Juzgado De Letras Y Garantia De Litueche"},
    {"cod_tribunal": "3643301", "tipo_juzgado": "8", "nombre_tribunal": "Juzgado De Letras Y Garantia De Peralillo"},

    #C.A. de Talca
    {"cod_tribunal": "3903301", "tipo_juzgado": "8", "nombre_tribunal": "1º Juzgado De Letras De Talca"},
    {"cod_tribunal": "3903302", "tipo_juzgado": "8", "nombre_tribunal": "2º Juzgado De Letras De Talca"},
    {"cod_tribunal": "3903303", "tipo_juzgado": "8", "nombre_tribunal": "3º Juzgado De Letras De Talca"},
    {"cod_tribunal": "3903304", "tipo_juzgado": "8", "nombre_tribunal": "4º Juzgado De Letras De Talca"},
    {"cod_tribunal": "3973301", "tipo_juzgado": "8", "nombre_tribunal": "Juzgado De Letras De Constitucion"},

]

fechas = ["04-10-2024", "03-10-2024", "02-10-2024", "01-10-2024", "30-09-2024"]


for tribunal in tribunales:
    data = []
    print(f"*Procesando datos de {tribunal['nombre_tribunal']}...")
    for fecha in fechas:
        # Payload data
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

        # Locate the specific div and table by their ids
        competencia_laboral_div = soup.find("div", id="competencia-laboral")

        if competencia_laboral_div:
            print(f"  - Fecha: {fecha} - OK")
            table = competencia_laboral_div.find("table", id="data-table-estado-diario-laboral")

            # Extract table headers
            headers = [header.text.strip() for header in table.find_all("th")]

            # Extract table rows
            for row in table.find_all("tr")[1:]:  # Skip header row
                columns = [col.text.strip() for col in row.find_all("td")]
                data.append(columns + [tribunal["nombre_tribunal"], fecha])
        else:
            # Print message to console if no data is found
            print(f"  - Fecha: {fecha} - no hay datos")
    
    # Convert the list to a DataFrame
    if data:
        headers.extend(["TRIBUNAL", "Fecha"])
        df = pd.DataFrame(data, columns=headers)

        # Save the DataFrame to an Excel file named after the first tribunal's nombre_tribunal
        file_name = f"{tribunal['nombre_tribunal'].replace(' ', '_')}.xlsx"
        df.to_excel(file_name, index=False)
        print(f"Estados diarios guardados en '{file_name}'")
    else:
        print(f"No hay estados diarios para {tribunal['nombre_tribunal']}.")