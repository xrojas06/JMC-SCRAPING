import json
import pandas as pd
import http.client


def scrape_page_playwright_and_save_sheet(url_path, filename):
    first = 100
    after = 0
    productos_list = []

    conn = http.client.HTTPSConnection("www.exito.com")

    headers = {
        'cookie': "az_botm=a7652dcf225c99273694d4d781cf1726; az_asm=8A0E2AA02D5F583B1AE57E97DC1558F1F1451464777D5AD5F57A20DAEADE69A37E2EE8CDCA55AFDE7CE3C4A6A39CC51119DA7E39BA51763626CE590B2C808943",
        'User-Agent': "insomnia/8.6.1"
    }

    while True:
        path = url_path.format(first, after)
        conn.request("GET", path, "", headers)
        res = conn.getresponse()
        data_text = res.read().decode('utf-8')

        if res.status == 200:
            productos = json.loads(data_text).get('data', {}).get('search', {}).get('products', {}).get('edges', [])

            if not productos:
                break

            for producto in productos:
                node = producto.get('node', {})

                nombre = node.get('name', '')
                tipo = node.get('productType',{}).get('type','')
                marca = node.get('brand', {}).get('brandName', '')
                categoria = node.get('breadcrumbList', {}).get('itemListElement')[1].get('name', 0)

                if len(node.get('sellers', {})):
                    precio_promocional = node.get('sellers', {})[0].get('commertialOffer', {}).get('Price', 0)
                    precio_sin_descuento = node.get('sellers', {})[0].get('commertialOffer', {}).get(
                        'PriceWithoutDiscount', 0)
                else:
                    precio_promocional = 'No disponible'
                    precio_sin_descuento = 'No disponible'

                url = 'https://www.exito.com' + \
                    node.get('breadcrumbList', {}).get('itemListElement')[-1].get('item', 0)


                print(tipo,marca,categoria,nombre,precio_sin_descuento, precio_promocional)
                productos_list.append(
                    [url,tipo,marca,categoria,nombre,precio_sin_descuento, precio_promocional])

            print(after)
            after += first

        else:
            print("Error al obtener los productos:", res.status)
            break

    conn.close()

    df = pd.DataFrame(productos_list, columns=[
                      'URL','Tipo','Marca','Categoría' ,'Nombre', 'Precio Regular', 'Precio Promocional'])

    return df




paths_and_filenames = [
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
     "General"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwOTM%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
      "Suba"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwODM%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
     "Villa Mayor"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwODY%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
     "Calle 80"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22orders_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwNjM%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
    "Pereira Victoria"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2w0MDU4%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
    "Cali Valle De Lili"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22orders_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwMzc%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
    "Medellin Laureles"),
    ("/api/gra0hql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwMzA%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
    "Bello"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wzNTc%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
    "Monteria Alamedas Del Sinu"),
    ("/api/graphql?operationName=ProductsQuery&variables=%7B%22first%22%3A{0}%2C%22after%22%3A%22{1}%22%2C%22sort%22%3A%22score_desc%22%2C%22term%22%3A%22%22%2C%22selectedFacets%22%3A%5B%7B%22key%22%3A%22productClusterIds%22%2C%22value%22%3A%225656%22%7D%2C%7B%22key%22%3A%22channel%22%2C%22value%22%3A%22%7B%5C%22salesChannel%5C%22%3A%5C%221%5C%22%2C%5C%22regionId%5C%22%3A%5C%22U1cjZXhpdG9jb2w7ZXhpdG9jb2wwNDc%3D%5C%22%7D%22%7D%2C%7B%22key%22%3A%22locale%22%2C%22value%22%3A%22es-CO%22%7D%5D%7D",
    "Barranquilla Metropolitano")
]



with pd.ExcelWriter('exito_insuperables_2204.xlsx') as writer:
    for path,file in paths_and_filenames:
        print(file)
        df = scrape_page_playwright_and_save_sheet(path, 'exito_insuperables_2204.xlsx')
        df.to_excel(writer, sheet_name=f'{file}', index=False)
