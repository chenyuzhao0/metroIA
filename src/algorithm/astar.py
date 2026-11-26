import heapq
from src.model.grafo import construir_adyacencia,obtener_coordenadas,obtener_vecinos
from src.algorithm.heuristica import heuristica_tiempo_min

def calcular_ruta_astar(parametros,heuristica=heuristica_tiempo_min):
    origen = parametros["origen"]
    destino = parametros["destino"]
    datos_red = parametros["datos_red"]
    estaciones = datos_red["estaciones"]
    adyacencia = construir_adyacencia(datos_red)
    if estaciones[origen].get("cortada", False) or estaciones[destino].get("cortada", False):
        return {"ruta":[], "tiempo_total": None, "transbordos": [], "coste_g": None, "nodos_expandidos":0}
    coord_destino = obtener_coordenadas(estaciones,destino)

    abierta = []
    cerrada = set()
    g_score = {origen: 0.0}
    padres = {origen: None}
    contador = 0
    nodos_expandidos = 0
    h_inicial = heuristica(obtener_coordenadas(estaciones,origen),coord_destino)
    heapq.heappush(abierta,(h_inicial,0.0,contador,origen))

    while abierta:
        f_actual, g_actual, _, actual = heapq.heappop(abierta)
        if actual in cerrada:
            continue
        if actual == destino:
            break
        cerrada.add(actual)
        nodos_expandidos += 1
        for vecino,coste_arista, _ in obtener_vecinos(estaciones,adyacencia,actual,parametros):
            if vecino in cerrada:
                continue
            nuevo_g = g_actual + coste_arista
            if vecino not in g_score or nuevo_g < g_score[vecino]:
                g_score[vecino] = nuevo_g
                padres[vecino] = actual
                h_val = heuristica(obtener_coordenadas(estaciones,vecino),coord_destino)
                contador += 1
                heapq.heappush(abierta,(nuevo_g + h_val, nuevo_g, contador, vecino))


    if destino not in padres:
        return {"ruta":[], "tiempo_total": None, "transbordos": [],"coste_g": None, "nodos_expandidos":nodos_expandidos}

    ruta = []
    nodo = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = padres[nodo]

    ruta.reverse()

    transbordos = []
    for i in range(len(ruta)-1):
        u = ruta[i]
        v = ruta[i+1]
        if estaciones[u]["linea"] != estaciones[v]["linea"]:
            transbordos.append(f"{estaciones[u]['nombre']} (L{estaciones[u]['linea']} -> L{estaciones[v]['linea']})")

    return {
        "ruta": ruta,
        "tiempo_total": g_score[destino],
        "transbordos": transbordos,
        "coste_g": g_score[destino],
        "nodos_expandidos": nodos_expandidos,
    }