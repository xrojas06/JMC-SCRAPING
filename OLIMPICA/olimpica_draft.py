import base64
import json
import time
import urllib.parse  # Importar el módulo para codificar URL
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

# Leer el archivo Excel y obtener las URLs
excel_filename = 'Chequeo WEB Olimpica W17.xlsx'  # Nombre del archivo Excel con las URLs
df_urls = pd.read_excel(excel_filename, skiprows=1)  # Leer el archivo Excel, omitiendo la primera fila (encabezados)

# Crear una lista vacía para almacenar los datos extraídos
data_list = []

# URL base para la solicitud GraphQL
url_graphql_base = (
    "https://www.olimpica.com/_v/segment/graphql/v1"
    "?workspace=master&maxAge=short&appsEtag=remove&domain=store"
    "&locale=es-CO&__bindingId=6e864c25-6c9e-4bf6-84e0-a4c1f4d151e4"
    "&operationName=getProductInfo"
    "&variables={{}}"
    "&extensions={{"
        "\"persistedQuery\":{{"
            "\"version\":1,"
            "\"sha256Hash\":\"7fb2d54cb37a58cdcedc746fbb2fc46ddc1aff8a156ddd1d246deaaf93ce8de6\","
            "\"sender\":\"olimpica.dinamic-flags@0.x\","
            "\"provider\":\"vtex.search-graphql@0.x\""
        "}},"
        "\"variables\":\"{cadena_base64_nueva}\""
    "}}"
)

# Iterar sobre las URLs con tqdm para mostrar la barra de progreso
for url in tqdm(df_urls['LINK'], desc="Procesando URLs"):
    # Realizar una solicitud HTTP para obtener el HTML de la página
    response_html = requests.get(url)
    html_content = response_html.content

    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraer el ID del producto del HTML utilizando la clase especifica
    span_element = soup.find('span', class_='vtex-product-identifier-0-x-product-identifier__value')
    id_producto = span_element.text if span_element else None

    # Si se encuentra un ID de producto, procesarlo
    if id_producto:
        # Crear un objeto JSON con el ID del producto
        x = f'{{"id":"{id_producto}"}}'

        # Convertir el objeto JSON a una cadena Base64
        cadena_json_nueva = json.dumps(json.loads(x), separators=(',', ':')).encode('utf-8')
        cadena_base64_nueva = base64.b64encode(cadena_json_nueva).decode('utf-8')

        # Codificar la cadena Base64 para su uso en la URL
        cadena_base64_nueva_coded = urllib.parse.quote(cadena_base64_nueva)

        # Reemplazar la variable `cadena` en la URL base con la cadena codificada
        url_graphql = url_graphql_base.format(cadena_base64_nueva=cadena_base64_nueva)

        # Realizar la solicitud a la API GraphQL
        response_json = requests.get(url_graphql)
        data_json = response_json.json()

        # Si la respuesta contiene datos del producto, extraer los datos
        if 'data' in data_json and 'product' in data_json['data']:
            product_data = data_json['data']['product']
            product_name = product_data.get('productName')
            sellers = product_data.get('items', [])[0].get('sellers', [])
            price = sellers[0]['commertialOffer'].get('Price', None) if sellers else None
            list_price = sellers[0]['commertialOffer'].get('ListPrice', None) if sellers else None

        # Almacenar los datos extraídos en la lista
        data_list.append({
                'Url': url,
                'Nombre': product_name,
                'Precio Promocional': price,
                'Precio Regular': list_price
            })

        # # Imprimir los datos extraídos del producto
        # print('Nombre: ', product_name,
        #       'Precio Promocional: ', price,
        #       'Precio Regular: ', list_price)
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
output_excel_filename = 'productos_olimpica_w17.xlsx'  # Nombre del archivo Excel de salida
data_df.to_excel(output_excel_filename, index=False)  # Guardar el DataFrame en el archivo Excel

# Imprimir un mensaje indicando que los datos se guardaron correctamente
print(f'Datos guardados en {output_excel_filename}')
