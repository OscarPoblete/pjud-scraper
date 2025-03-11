### Scraper Pjud
Conjunto de scripts en Python para hacer web scraping del sitio web del Poder Judicial de Chile y obtener estados diarios de tribunales de primera instancia.

### Prerrequisitos
- requests
- beautifulsoup4
- pandas
- openpyxl
- selenium

### Modo de uso
Ejecutar **pjud-tribunales.py** para obtener los códigos de todos los tribunales, que luego son utilizados por los demás scripts.
Luego, con **pjud-civil.py**, **pjud-penal.py**, etc. se obtienen los estados diarios en el rango de fechas especificado dentro del script, en un archivo excel.
