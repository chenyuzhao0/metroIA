from math import radians, sin, cos, sqrt,atan2


def distancia_haversine_km(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1,lon1,lat2,lon2 = map(radians, [lat1, lon1, lat2, lon2]);
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    a = min(1.0,max(0.0,a))
    c = 2 * atan2(sqrt(a),sqrt(1-a))
    return 6371.0 * c

def heuristica_tiempo_min(coord_actual, coord_destino, v_max_kmh=80.0):
    if(v_max_kmh <= 0):
        raise ValueError("v_max_kmh deberia de ser mayor de 0")
    distancia = distancia_haversine_km(coord_actual, coord_destino)
    return (distancia / v_max_kmh) * 60.0
    
def heuristica_cero(coord_actual, coord_destino):
    return 0.0

