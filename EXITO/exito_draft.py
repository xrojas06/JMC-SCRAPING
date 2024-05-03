import base64
import http.client
import json
import time
import urllib.parse  # Importar el módulo para codificar URL
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re


# Leer el archivo Excel y obtener las URLs
excel_filename = 'Chequeo WEB Exito W17.xlsx'  # Nombre del archivo Excel con las URLs
df_urls = pd.read_excel(excel_filename, skiprows=1)  # Leer el archivo Excel, omitiendo la primera fila (encabezados)

# Crear una lista vacía para almacenar los datos extraídos
data_list = []

# URL base para la solicitud GraphQL
url_graphql_base = "/api/graphql?operationName=BrowserProductQuery&variables=%7B%22locator%22%3A%5B%7B%22key%22%3A%22id%22%2C%22value%22%3A%22{0}%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwOTM%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D"
conn = http.client.HTTPSConnection("www.exito.com")

# Iterar sobre las URLs con tqdm para mostrar la barra de progreso
for url in tqdm(df_urls['LINK'], desc="Procesando URLs"):
    # Realizar una solicitud HTTP para obtener el HTML de la página
    response_html = requests.get(url)
    html_content = response_html.content

    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraer el ID del producto del HTML utilizando la clase especifica
    span_element = soup.find('span', class_='product-title_product-title__specification__B5pYV')
    id_producto = re.findall(r'\d+', span_element.text)
    id_producto = int(id_producto[0]) if id_producto else None

    # Si se encuentra un ID de producto, procesarlo
    if id_producto:
        # Crear un objeto JSON con el ID del producto

        # Reemplazar la variable `cadena` en la URL base con la cadena codificada
        url_graphql = url_graphql_base.format(id_producto)
        print(url_graphql)
        payload = ""

        headers = {'User-Agent': "insomnia/9.1.0"}

        conn.request("GET",
                     url_graphql,
                     payload, headers)

        # Realizar la solicitud a la API GraphQL
        response = conn.getresponse()
        data = response.read().decode('utf-8')

        # Convierte la cadena JSON en un diccionario de Python
        data_json = json.loads(data)

        # Si la respuesta contiene datos del producto, extraer los datos
        if 'data' in data_json and 'product' in data_json['data']:
            product_data = data_json['data']['product']
            product_name = product_data.get('name')
            offers = product_data.get('offers', []).get('offers', [])
            price = offers[0].get('price', None) if offers else None
            list_price = offers[0].get('listPrice', None) if offers else None

        # Almacenar los datos extraídos en la lista
        data_list.append({
                'Url': url,
                'Nombre': product_name,
                'Precio Promocional': price,
                'Precio Regular': list_price
            })

        # # Imprimir los datos extraídos del producto
        print('Nombre: ', product_name,
               'Precio Promocional: ', price,
               'Precio Regular: ', list_price)
    else:
        # Si no se encontró un ID de producto, imprimir un mensaje de error
        print('ERROR')
        data_list.append({
                'Url': url,
                'Nombre': 'ERROR',
                'Precio Promocional': 0,
                'Precio Regular': 0
            })

# Guardar el DataFrame con los datos extraídos en un nuevo archivo Excel
data_df = pd.DataFrame(data_list)
output_excel_filename = 'productos_exito_w17.xlsx'  # Nombre del archivo Excel de salida
data_df.to_excel(output_excel_filename, index=False)  # Guardar el DataFrame en el archivo Excel

# Imprimir un mensaje indicando que los datos se guardaron correctamente
print(f'Datos guardados en {output_excel_filename}')
