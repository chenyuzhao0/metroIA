from src.algorithm.heuristica import distancia_haversine_km

def obtener_coordenadas(estaciones, est_id):
    est = estaciones[est_id]
    return (est["lat"], est["lon"])

def construir_adyacencia(datos_red):
    adyacencia = {}
    for est_id in datos_red["estaciones"]:
        adyacencia[est_id] = []
    for c in datos_red["conexiones"]:
        origen = c["origen"]
        destino = c["destino"]
        cortada = c.get("cortada", False)
        adyacencia[origen].append({"destino": destino,"tipo":"tramo", "cortada": cortada})
        adyacencia[destino].append({"destino": origen,"tipo":"tramo", "cortada": cortada})

    for t in datos_red["transbordos"]:
        origen = t["origen"]
        destino = t["destino"]
        cortada = t.get("cortada", False)
        adyacencia[origen].append({"destino": destino, "tipo": "transbordo","longitud_m":t.get("longitud_m",100),
                                   "ascensor":t.get("ascensor",True),"escaleras":t.get("escaleras",0),"cortada": cortada})
        adyacencia[destino].append({"destino": origen, "tipo": "transbordo","longitud_m":t.get("longitud_m",100),
                                   "ascensor":t.get("ascensor",True),"escaleras":t.get("escaleras",0),"cortada": cortada})

    return adyacencia

def obtener_vecinos(estaciones, adyacencia, nodo_actual, opciones):
    if estaciones[nodo_actual].get("cortada", False):
        return []

    resultado = []
    for arista in adyacencia[nodo_actual]:
        vecino = arista["destino"]
        if arista["cortada"] or estaciones[vecino].get("cortada", False):
            continue
        if arista["tipo"] == "tramo":
            dist_km = distancia_haversine_km(obtener_coordenadas(estaciones, nodo_actual), obtener_coordenadas(estaciones, vecino))
            tiempo_viaje = (dist_km / 38.0) * 60
            tiempo_parada = opciones.get("tiempo_parada_min",0.5)
            afluencia = opciones.get("afluencia","media")
            aforo = estaciones[vecino].get("aforo",50)
            if afluencia == "alta":
                extra_afluencia = (aforo / 100.0) * 0.8
            elif afluencia == "media":
                extra_afluencia = (aforo / 100.0) * 0.3
            else:
                extra_afluencia = 0.0
            if opciones.get("movilidad_reducida",False) and not estaciones[vecino].get("ascensor",True):
                extra_movilidad = estaciones[vecino].get("escaleras",0)*0.5
            else:
                extra_movilidad = 0.0
            coste = tiempo_viaje + extra_afluencia + extra_movilidad + tiempo_parada
        else:
            base = float(opciones.get("penalizacion_transbordo",4.00))
            extra_longitud = arista.get("longitud_m",100) /100.0
            if opciones.get("afluencia") == "alta":
                extra_afluencia = 1.0
            else:
                extra_afluencia = 0.0
            if opciones.get("movilidad_reducida",False):
                if not arista.get("ascensor",True):
                    continue
                extra_movilidad = arista.get("escaleras",0)*0.5
            else:
                extra_movilidad = 0.0

            coste = base + extra_afluencia + extra_movilidad + extra_longitud
        resultado.append((vecino,coste,arista["tipo"]))

    return resultado