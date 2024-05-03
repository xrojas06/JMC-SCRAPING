import requests
from bs4 import BeautifulSoup
import pandas as pd
import re  # Importar el módulo de expresiones regulares

# Lista para almacenar los datos
datos = []

# Función para recorrer una categoría y sus productos
def procesar_categoria(nombre_categoria, url_categoria, categoria_padre=None):
    nombre_categoria_completo = nombre_categoria

    # Manejar la paginación dentro de la categoría
    pagina_actual = 1
    while True:
        # Generar la URL para la página actual dentro de la categoría
        url_pagina = f"{url_categoria}?product-page={pagina_actual}"

        # Realizar la solicitud HTTP para obtener la página
        response = requests.get(url_pagina)

        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            print(f"No se pudo obtener la página {pagina_actual} de la categoría {nombre_categoria}.")
            break

        # Analizar el HTML de la página actual
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer los productos de la página actual
        productos = soup.find_all('li', class_='product')
        for producto in productos:
            # Extraer datos del producto
            nombre_producto = producto.find('h2', class_='woocommerce-loop-product__title').text.strip()

            # Extraer precios de los productos
            precio_elementos = producto.find_all('span', class_='woocommerce-Price-amount amount')
            if len(precio_elementos) > 1:
                precio_regular = precio_elementos[0].text.strip()
                precio_promocional = precio_elementos[1].text.strip()
            else:
                precio_regular = precio_elementos[0].text.strip()
                precio_promocional = precio_regular

            # Extraer URL del producto
            url_producto = producto.find('a', class_='woocommerce-LoopProduct-link').get('href')

            # Obtener datos adicionales del producto
            sku, categoria, marca = obtener_datos_producto(url_producto)

            # Guardar los datos del producto, incluyendo categoría y subcategoría
            datos.append({
                "nombre_categoria": eliminar_parentesis(nombre_categoria_completo),
                "subcategoria": eliminar_parentesis(categoria),
                "marca": marca,
                "nombre_producto": nombre_producto,
                "precio_regular": precio_regular,
                "precio_promocional": precio_promocional,
                "url_producto": url_producto,
                "SKU": sku,
            })

        # Verificar si hay una página siguiente
        next_page = soup.find('a', class_='next page-numbers')
        if next_page:
            pagina_actual += 1
        else:
            # No hay más páginas, salir del bucle
            break

# Función para obtener los datos adicionales de un producto
def obtener_datos_producto(url_producto):
    # Realizar la solicitud HTTP para obtener la página del producto
    response = requests.get(url_producto)

    # Verificar si la solicitud fue exitosa
    if response.status_code != 200:
        print(f"No se pudo obtener la página del producto {url_producto}.")
        return None, None, None, None

    # Analizar el HTML de la página del producto
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer datos adicionales
    sku_element = soup.find('span', class_='sku')
    sku = sku_element.text.strip() if sku_element else None

    # Extraer categoría
    posted_in_elements = soup.find_all('span', class_='posted_in')

    # Inicializar variables para categoría y marca
    categoria = None
    marca = None

    # Diferenciar entre categoría y marca
    for element in posted_in_elements:
        text = element.text.strip()
        print('TEXT: ',text)
        if  'Categ' in text :
            # Extraer las categorías
            categorias = [a.text for a in element.find_all('a')]
            categoria = categorias[0]
        elif 'arca:' in text:
            # Extraer la marca
            marca = element.find('a').text

    print(sku,categoria,marca)
    return sku, categoria, marca

# Función para eliminar los números entre paréntesis
def eliminar_parentesis(texto):
    # Utilizar una expresión regular para eliminar el contenido entre paréntesis
    return re.sub(r'\s*\(\d+\)', '', texto)

# URL de la página con categorías y subcategorías
url_base = "https://tiendasisimo.com/mercado/"

# Realizar la solicitud HTTP para obtener el HTML de la página base
response = requests.get(url_base)

# Verificar si la solicitud fue exitosa (código de estado 200)
if response.status_code != 200:
    raise Exception(f"No se pudo obtener la página base. Código de estado: {response.status_code}")

# Crear un objeto BeautifulSoup para analizar el HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Encontrar las categorías principales
categorias_principales = soup.find_all('ul', class_='sidebar-categories-list')

for categoria in categorias_principales:
    categoria_items = categoria.find_all('li', recursive=False)
    print('CATEGORIA PRINCIPAL: ', categoria.text)
    for item in categoria_items:
        print('SUBCATEGORIA: ', item.text)
        # Extraer enlace y nombre de la categoría
        link = item.find('a')
        if link:
            url_categoria = link.get('href')
            nombre_categoria = link.text.strip()
            print(nombre_categoria)

            procesar_categoria(nombre_categoria, url_categoria)

# Crear un DataFrame con los datos extraídos
df = pd.DataFrame(datos)

# Guardar el DataFrame como un archivo Excel
df.to_excel('barrido_isimo.xlsx', index=False)

print("Los datos han sido guardados en 'barrido_isimo.xlsx'.")
