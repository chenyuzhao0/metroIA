import copy,json,os,unittest

from src.algorithm.astar import calcular_ruta_astar
from src.algorithm.heuristica import (
    distancia_haversine_km,
    heuristica_cero,
    heuristica_tiempo_min,
)
from src.model.grafo import construir_adyacencia, obtener_coordenadas, obtener_vecinos


RUTA_DATOS = os.path.join(os.path.dirname(__file__), "..", "data", "estaciones.json")


class TestAStarMetrorrey(unittest.TestCase):
    def setUp(self):
        with open(RUTA_DATOS, "r", encoding="utf-8") as f:
            self.datos = json.load(f)

    def _parametros(self, origen, destino, datos=None, **extras):
        params = {
            "origen": origen,
            "destino": destino,
            "datos_red": datos if datos is not None else self.datos,
            "afluencia": "media",
            "movilidad_reducida": False,
            "penalizacion_transbordo": 5.0,
            "tiempo_parada_min": 0.5,
        }
        params.update(extras)
        return params

    def test_misma_estacion(self):
        res = calcular_ruta_astar(self._parametros("Talleres_L1", "Talleres_L1"))
        self.assertEqual(res["ruta"], ["Talleres_L1"])
        self.assertEqual(res["coste_g"], 0.0)
        self.assertEqual(res["transbordos"], [])
        self.assertEqual(res["nodos_expandidos"], 0)

    def test_misma_linea_sin_transbordos(self):
        res = calcular_ruta_astar(self._parametros("Talleres_L1", "Exposicion_L1"))
        self.assertEqual(res["ruta"][0], "Talleres_L1")
        self.assertEqual(res["ruta"][-1], "Exposicion_L1")
        self.assertEqual(len(res["ruta"]), 19)
        self.assertEqual(res["transbordos"], [])
        self.assertGreater(res["coste_g"], 0.0)

    def test_ruta_con_transbordo(self):
        res = calcular_ruta_astar(
            self._parametros("Talleres_L1", "Hospital_Metropolitano_L3")
        )
        self.assertEqual(res["ruta"][0], "Talleres_L1")
        self.assertEqual(res["ruta"][-1], "Hospital_Metropolitano_L3")
        self.assertEqual(len(res["transbordos"]), 1)
        self.assertIn("Félix U. Gómez", res["transbordos"][0])

    def test_desvio_por_estacion_cortada(self):
        datos_corte = copy.deepcopy(self.datos)
        datos_corte["estaciones"]["Del_Golfo_L1"]["cortada"] = True

        res = calcular_ruta_astar(
            self._parametros("Talleres_L1", "Exposicion_L1", datos=datos_corte)
        )
        self.assertTrue(len(res["ruta"]) > 0)
        self.assertNotIn("Del_Golfo_L1", res["ruta"])
        self.assertEqual(res["ruta"][0], "Talleres_L1")
        self.assertEqual(res["ruta"][-1], "Exposicion_L1")
        self.assertGreaterEqual(len(res["transbordos"]), 2)

    def test_destino_cortado_sin_ruta(self):
        datos_corte = copy.deepcopy(self.datos)
        datos_corte["estaciones"]["Exposicion_L1"]["cortada"] = True

        res = calcular_ruta_astar(
            self._parametros("Talleres_L1", "Exposicion_L1", datos=datos_corte)
        )
        self.assertEqual(res["ruta"], [])
        self.assertIsNone(res["coste_g"])
        self.assertIsNone(res["tiempo_total"])

    def test_movilidad_reducida_paso_intermedio_y_bloqueo(self):
        # Origen y destino accesibles en L2: el tren puede pasar por estaciones subterráneas intermedias
        res_ok = calcular_ruta_astar(
            self._parametros("Universidad_L2", "Cuauhtemoc_L2", movilidad_reducida=True)
        )
        self.assertEqual(len(res_ok["ruta"]), 5)
        self.assertEqual(res_ok["transbordos"], [])

        # Destino subterráneo sin ascensor (Alameda_L2): debe rechazar la ruta
        res_no = calcular_ruta_astar(
            self._parametros("Sendero_L2", "Alameda_L2", movilidad_reducida=True)
        )
        self.assertEqual(res_no["ruta"], [])
        self.assertIsNone(res_no["coste_g"])
        self.assertIn("mensaje_error", res_no)

    def test_heuristica_haversine_y_validacion(self):
        c1 = obtener_coordenadas(self.datos["estaciones"], "Talleres_L1")
        c2 = obtener_coordenadas(self.datos["estaciones"], "Exposicion_L1")
        self.assertEqual(distancia_haversine_km(c1, c1), 0.0)
        self.assertGreater(distancia_haversine_km(c1, c2), 10.0)
        self.assertGreater(heuristica_tiempo_min(c1, c2), 0.0)
        with self.assertRaises(ValueError):
            heuristica_tiempo_min(c1, c2, v_max_kmh=0)

    def test_consistencia_heuristica_todos_los_modos(self):
        estaciones = self.datos["estaciones"]
        adyacencia = construir_adyacencia(self.datos)

        for afluencia in ("baja", "media", "alta"):
            for mov in (False, True):
                for pen in (0.0, 5.0, 15.0):
                    opts = {
                        "afluencia": afluencia,
                        "movilidad_reducida": mov,
                        "penalizacion_transbordo": pen,
                        "tiempo_parada_min": 0.5,
                    }
                    for u in estaciones:
                        cu = obtener_coordenadas(estaciones, u)
                        for v, coste, _ in obtener_vecinos(estaciones, adyacencia, u, opts):
                            cv = obtener_coordenadas(estaciones, v)
                            h_uv = heuristica_tiempo_min(cu, cv)
                            self.assertLessEqual(
                                h_uv,
                                coste + 1e-9,
                                f"Consistencia violada en {u} -> {v} ({afluencia}, mov={mov})",
                            )

    def test_optimalidad_y_eficiencia_vs_dijkstra(self):
        rutas_prueba = [
            ("Talleres_L1", "Exposicion_L1"),
            ("Talleres_L1", "Hospital_Metropolitano_L3"),
            ("Sendero_L2", "Exposicion_L1"),
            ("Sendero_L2", "Hospital_Metropolitano_L3"),
            ("Zaragoza_L2", "Mitras_L1"),
        ]
        for origen, destino in rutas_prueba:
            params = self._parametros(origen, destino)
            res_astar = calcular_ruta_astar(params, heuristica=heuristica_tiempo_min)
            res_dijkstra = calcular_ruta_astar(params, heuristica=heuristica_cero)

            self.assertAlmostEqual(res_astar["coste_g"], res_dijkstra["coste_g"], places=6)
            self.assertLessEqual(
                res_astar["nodos_expandidos"], res_dijkstra["nodos_expandidos"]
            )


if __name__ == "__main__":
    unittest.main()
