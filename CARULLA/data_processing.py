import json
import pandas as pd
import http.client
from http_requests import generate_data_request

def scraping_category(category, categories,base_json):
    first = 0
    after = 1000
    productos_list = []

    while True:

        data_text = generate_data_request(category, categories, base_json, first, after)

        if len(data_text) > 1000:
            print("ENTRE")
            productos = json.loads(data_text).get('data', {}).get('productSearch', {}).get('products', {})
            if not productos:
                break
            for producto in productos:
                nombre = producto.get('productName', '')
                marca = producto.get('brand', {})
                categoria = producto.get('categories', [])[-1].replace('/','')

                if len(producto.get('priceRange', {})):
                    precio_promocional = producto.get('priceRange', {}).get('sellingPrice', {}).get('highPrice', None)
                    precio_sin_descuento = producto.get('priceRange', {}).get('listPrice', {}).get('highPrice', None)
                else:
                    precio_promocional = 'No disponible'
                    precio_sin_descuento = 'No disponible'

                url = 'https://www.carulla.com' + \
                      producto.get('link', '')

                print(categoria, marca, nombre, precio_sin_descuento, precio_promocional)

                productos_list.append(
                    [url, categoria, marca, nombre, precio_sin_descuento, precio_promocional])


            after += first
        else:
            print("Sali por error")
            break

    # print("PRODUCTOS")
    # print(productos_list)
    df = pd.DataFrame(productos_list, columns=[
                      'URL','Categoría','Marca' ,'Nombre', 'Precio Regular', 'Precio Promocional'])

    return df