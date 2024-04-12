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
import re


def scrape_page_playwright(links, is_exito=True):
            productos_list = []
            for i in tqdm(links):
                url = i

                conn = http.client.HTTPSConnection("www.exito.com")

                headers = {
                    'cookie': "az_botm=a7652dcf225c99273694d4d781cf1726; az_asm=8A0E2AA02D5F583B1AE57E97DC1558F1F1451464777D5AD5F57A20DAEADE69A37E2EE8CDCA55AFDE7CE3C4A6A39CC51119DA7E39BA51763626CE590B2C808943",
                    'User-Agent': "insomnia/8.6.1"
                }



                response = requests.get(url)
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                product_title_span = soup.find('span', class_='product-title_product-title__specification__B5pYV')

                if product_title_span:
                    product_title = product_title_span.text.strip()
                    numero = re.search(r'\d+', product_title).group()
                else:
                    numero = re.search(r'(\d+)/p', url).group(1)

                path = f"/api/graphql?operationName=BrowserProductQuery&variables=%7B%22locator%22%3A%5B%7B%22key%22%3A%22id%22%2C%22value%22%3A%22{numero}%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwOTM%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D"
                conn.request("GET", path, "", headers)
                res = conn.getresponse()
                #data = res.read()
                data_text = res.read().decode('utf-8')

                if res.status == 200:
                    producto = json.loads(data_text).get('data', {}).get('product', {})

                    if not producto:
                        break

                    nombre = producto.get('name', '')

                    if len(producto.get('sellers', {})):
                        precio = producto.get("sellers", [{}])[0].get("commertialOffer", {}).get("Price")
                        precio_sin_descuento = producto.get("sellers", [{}])[0].get("commertialOffer", {}).get("PriceWithoutDiscount")
                    else:
                        precio = 'No disponible'
                        precio_sin_descuento = 'No disponible'

                    print(nombre, precio, precio_sin_descuento)
                    productos_list.append([url,nombre, precio, precio_sin_descuento])

                else:
                    print("Error al obtener los productos:", res.status)
                    continue

            conn.close()
            df = pd.DataFrame(productos_list, columns=[ 'URL','Nombre', 'Precio', 'Precio_Descuento'])

            return df

links = pd.read_excel('Links.xlsx', skiprows=1)['LINK']
print(links)

df = scrape_page_playwright(links)
df.to_excel('exito_suba.xlsx')
print(df)