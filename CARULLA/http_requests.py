import base64
import json
import http.client


def generate_data_request(category, categories,base_json, first, after):

    """
    Genera una solicitud de datos para la categoría especificada utilizando el diccionario base_json como base.

    Argumentos:
        category (str): La categoría para la cual se generará la solicitud de datos.
        base_json (dict): Diccionario base que contiene los parámetros iniciales para la solicitud.

    Devuelve:
        str: Cuerpo de la respuesta de la solicitud HTTP.
    """

    # Actualiza el valor de la clave "query" en base_json con la categoría especificada, envuelta en comillas simples
    print("CATEGORIA: ", category)
    data = categories[category]
    base_json["query"] = data['value']
    base_json["first"] = int(f"{first}")
    base_json["after"] = int(f"{after}")
    base_json["selectedFacets"][0]["value"] = data['value']
    base_json["map"] = data['map']
    base_json["selectedFacets"][0]["key"] = data['map']

    if data['Tree'] == 0:
        base_json.pop("categoryTreeBehavior", None)
    else:
        # Si 'tree' es 1, agrega "categoryTreeBehavior" si no está presente
        if "categoryTreeBehavior" not in base_json:
            base_json["categoryTreeBehavior"] = "default"


    # Convierte base_json en una cadena JSON comprimida
    cadena_json_nueva = json.dumps(base_json, separators=(',', ':')).encode('utf-8')

    # Codifica la cadena JSON a base64
    code = base64.b64encode(cadena_json_nueva).decode('utf-8')

    # Establece la conexión HTTPS con el servidor www.carulla.com
    conn = http.client.HTTPSConnection("www.carulla.com")

    # Define los encabezados para la solicitud, incluyendo cookies y un User-Agent específico
    headers = {
        'cookie': "az_botm=216a6ff0c75a03d5c4214ed869eb538e; az_asm=B10CFF684D8CDC3910BC4BD32DC511E806667A28610CC670CDABC4246D6936825C498C4695557EE0E7BFA3B7B3C2EC7E2BF5D086D33EAC3B5B03ECAC32917F37; janus_sid=d373eb8c-dc61-4887-96ba-b0f32b5f62de",
        'User-Agent': "insomnia/9.0.0"
    }

    # Define la URL base para la solicitud
    url_base = '/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove&domain=store&locale=es-CO&__bindingId=0ba72821-82ba-45f7-808b-a2a91d42e567&operationName=productSearchV3&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22fd92698fe375e8e4fa55d26fa62951d979b790fcf1032a6f02926081d199f550%22%2C%22sender%22%3A%22vtex.store-resources%400.x%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22'

    # Combina la URL base con el código base64 codificado y la cadena adicional para formar la URL final
    url_final = url_base + code + '%3D%22%7D'
    print(code)
    # Realiza una solicitud GET a la URL final con los encabezados especificados
    conn.request("GET", url_final, "", headers)

    # Obtiene la respuesta de la solicitud
    res = conn.getresponse()
    data_text = res.read().decode('utf-8')

    # Verifica si la respuesta indica un error (código de estado distinto de 200)
    if res.status != 200:
        return False

    conn.close()
    # Devuelve el cuerpo de la respuesta
    return data_text
