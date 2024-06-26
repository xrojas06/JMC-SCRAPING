import json

import requests
from openpyxl import Workbook
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import pandas as pd
import time
from playwright.sync_api import sync_playwright
from tqdm import tqdm
import http.client
import urllib.parse


def obtener_identificador_mas_reciente(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", {"src": lambda x: x and "_ssgManifest.js" in x})
        if script_tag:
            src = script_tag.get("src")
            # Extraer el identificador del src
            identificador = src.split("/")[3]  # Dividir por "/" y tomar el cuarto elemento
            return identificador
        else:
            print("No se encontró el script con el identificador.")
            return None
    else:
        print("Error al obtener la página:", response.status_code)
        return None

def scrape_page_playwright(is_exito = True):

    max_attempts = 2
    attempt = 0
    while attempt < max_attempts:
        with sync_playwright() as p:
                start_time = time.time()
                browser = p.chromium.launch()
                page = browser.new_page()

                if is_exito:

                    url = "https://www.exito.com/"
                    identificador = obtener_identificador_mas_reciente(url)

                    page.goto('https://www.exito.com/', timeout=600000)

                    page.click('div[data-fs-delivery-pin-container="true"]')

                    # Escribir "Bogotá" en el campo de selección de ciudad y presionar Enter
                    page.fill('input[id="react-select-2-input"]', 'Bogotá')
                    page.press('input[id="react-select-2-input"]', 'Enter')

                    # Esperar a que aparezca el campo de selección de tienda y escribir "Exito Suba", luego presionar Enter
                    page.fill('input[id="react-select-3-input"]', 'Éxito Usme')
                    page.press('input[id="react-select-3-input"]', 'Enter')

                    # Hacer clic en el botón de confirmar
                    page.click('button.PickupPoint_primaryButtonEnable__Z2OvB')
                    current_url = page.url

                    parsed_url = urllib.parse.urlparse(current_url)
                    host = parsed_url.hostname
                    port = parsed_url.port

                    if not port:
                        if parsed_url.scheme == 'https':
                            port = 443
                        else:
                            port = 80


                    conn = http.client.HTTPSConnection(host, port)

                    headers = {
                        'cookie': "az_botm=a7652dcf225c99273694d4d781cf1726; az_asm=8A0E2AA02D5F583B1AE57E97DC1558F1F1451464777D5AD5F57A20DAEADE69A37E2EE8CDCA55AFDE7CE3C4A6A39CC51119DA7E39BA51763626CE590B2C808943",
                        'User-Agent': "insomnia/8.6.1"
                    }

                    first = 100
                    after = 0
                    productos_list = []

                    '''

                    path_data = f"/_next/data/{identificador}/es-CO.json"
                    print(path_data)
                    conn.request("GET", f"/_next/data/{identificador}/es-CO.json","",headers)
                    response = conn.getresponse()
                    data = response.read()
                    data_text = json.loads(data)

                    paths = []
                    if response.status == 200:
                        second_container = data_text.get('pageProps', {}).get('globalProps', {}).get('sections', [{}])[3].get('data',{}).get('megaMenu',{}).get('secondContainer',{})

                        for item in second_container:
                            sublinks = item.get('subLinks',{})
                            for link in sublinks:
                                href = link.get('href')
                                path  = f"/_next/data/{identificador}/es-CO{href}.json"
                                paths.append(path)
                            #print('href: ',href)
                            #print('paths: ', paths)
                    '''

                    while True:
                        path = f"/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{first}%2C%22after%22%3A%22{after}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwNDE%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D"
                        path = f"/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{first}%2C%22after%22%3A%22{after}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwOTM%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D"
                        path = f"/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{first}%2C%22after%22%3A%22{after}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A1%2C%5C%22regionId%5C%22%3A%5C%22%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D"
                        conn.request("GET", path, "", headers)
                        res = conn.getresponse()
                        data = res.read()
                        data_text = res.read().decode('utf-8')
                        if res.status == 200:
                            productos = json.loads(data).get('data', {}).get('search', {}).get('products', {}).get(
                                'edges',
                                [])

                            if not productos:
                                break

                            for producto in productos:
                                node = producto.get('node', {})

                                nombre = node.get('name', '')
                                if len(node.get('sellers',{})):
                                    precio = node.get('sellers', {})[0].get('commertialOffer', {}).get('Price', 0)
                                    precio_descuento = node.get('sellers', {})[0].get('commertialOffer', {}).get('PriceWithoutDiscount', 0)
                                else:
                                    precio = 'No disponible'
                                    precio_descuento = 'No disponible'

                                url = 'https://www.exito.com' + node.get('breadcrumbList', {}).get('itemListElement')[-1].get('item', 0)

                                productos_list.append([nombre, precio, precio_descuento, url])

                            print(after)
                            after += first

                        else:
                            print("Error al obtener los productos:", res.status)
                            break

                    conn.close()

                    df = pd.DataFrame(productos_list, columns=['Nombre', 'Precio', 'Precio_Descuento', 'URL'])

        return df

df = scrape_page_playwright()
df.to_excel('exito_1.xlsx')
print(df)