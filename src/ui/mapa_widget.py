import os
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, Signal, QTimer

TIEMPO_TRAMO_SEG = 180.0   # 3 minutos entre estaciones
TIEMPO_PARADA_SEG = 30.0   # 30 segundos en cada estación
DT_FRAME_SEG = 0.05

AJUSTES_ETIQUETAS = {
    # Línea 1
    "Talleres_L1": (14, -10, 0),
    "San_Bernabe_L1": (14, -10, 0),
    "Unidad_Modelo_L1": (14, -10, 0),
    "Aztlan_L1": (14, -10, 0),
    "Penitenciaria_L1": (-108, -10, 0),
    "Alfonso_Reyes_L1": (-112, -10, 0),
    "Mitras_L1": (-62, -10, 0),
    "Simon_Bolivar_L1": (-114, -10, 0),
    "Hospital_L1": (-75, -10, 0),
    "Edison_L1": (-8, 14, 90),
    "Central_L1": (-8, 14, 90),
    "Cuauhtemoc_L1": (-48, -32, 0),
    "Del_Golfo_L1": (-28, -30, 0),
    "Felix_U_Gomez_L1": (14, -22, 0),
    "Parque_Fundidora_L1": (-10, 14, 90),
    "Y_Griega_L1": (-10, 14, 90),
    "Eloy_Cavazos_L1": (-10, 14, 90),
    "Lerdo_de_Tejeda_L1": (-10, 14, 90),
    "Exposicion_L1": (-10, 14, 90),

    # Línea 2
    "Sendero_L2": (-76, -10, 0),
    "Santiago_Tapia_L2": (-114, -10, 0),
    "San_Nicolas_L2": (-98, -10, 0),
    "Anahuac_L2": (-78, -10, 0),
    "Universidad_L2": (-96, -10, 0),
    "Ninos_Heroes_L2": (-106, -10, 0),
    "Regina_L2": (-66, -10, 0),
    "Gral_Anaya_L2": (-94, -10, 0),
    "Alameda_L2": (14, -10, 0),
    "Fundadores_L2": (-96, -10, 0),
    "Padre_Mier_L2": (-10, 14, 90),
    "Zaragoza_L2": (-10, 14, 90),

    # Línea 3
    "Santa_Lucia_L3": (-10, 14, 90),
    "Col_Obrera_L3": (-96, -10, 0),
    "Metalurgicos_L3": (14, -10, 0),
    "Col_Moderna_L3": (14, -10, 0),
    "Ruiz_Cortines_L3": (14, -10, 0),
    "Los_Angeles_L3": (14, -10, 0),
    "Hospital_Metropolitano_L3": (14, -14, 0),
}


class TrenAnimado:
    def __init__(self, linea, recorrido_ids, idx_estacion, progreso_tramo, sentido, item_grafico):
        self.linea = linea
        self.recorrido_ids = recorrido_ids
        self.idx_estacion = idx_estacion
        self.progreso_tramo = progreso_tramo
        self.sentido = sentido
        self.estado = "viajando"
        self.tiempo_espera_restante = 0.0
        self.item = item_grafico


class MapaMetrorreyView(QGraphicsView):
    estacion_clicada = Signal(str)          # Clic izquierdo: seleccionar origen/destino
    estacion_toggle_corte = Signal(str)     # Clic derecho: cortar/abrir estación

    def __init__(self, datos_red, ruta_imagen="assets/plano_metrorrey.png"):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.datos_red = datos_red
        self.estaciones = datos_red["estaciones"]
        self.conexiones = datos_red["conexiones"]
        self.items_ruta = []
        self.items_cortes = []
        self.items_monigote = []
        self.items_popup_info = []
        self.nodos_graficos = {}
        self.trenes = []
        self.servicio_activo = True

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 10px; background-color: #EAE5DC;")

        self._cargar_fondo_o_esquema(ruta_imagen)
        self._dibujar_estado_cortes()
        self._dibujar_nodos_y_nombres()
        self._iniciar_simulacion_trenes()

    def _cargar_fondo_o_esquema(self, ruta_imagen):
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            self.scene.addPixmap(pixmap)
            self.setSceneRect(pixmap.rect())
        else:
            self.setSceneRect(310, 120, 880, 760)
            self._dibujar_lineas_base()
            self._dibujar_leyenda_esquema()

    def _dibujar_lineas_base(self):
        colores_linea = {
            1: QColor("#F59E0B"),
            2: QColor("#16A34A"),
            3: QColor("#EA580C"),
        }
        for con in self.conexiones:
            est_o = self.estaciones.get(con["origen"])
            est_d = self.estaciones.get(con["destino"])
            if not est_o or not est_d:
                continue
            x1, y1 = est_o["px"]
            x2, y2 = est_d["px"]
            color = colores_linea.get(est_o["linea"], QColor("#64748B"))

            pen_via = QPen(color, 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            tramo = QGraphicsLineItem(x1, y1, x2, y2)
            tramo.setPen(pen_via)
            tramo.setZValue(2)
            self.scene.addItem(tramo)

    def _dibujar_leyenda_esquema(self):
        leyenda = QGraphicsTextItem(
            "SIMBOLOGÍA METRORREY\n"
            "🟡 Línea 1 (Talleres – Exposición)\n"
            "🟢 Línea 2 (Sendero – Gral. I. Zaragoza)\n"
            "🔴 Línea 3 (Gral. I. Zaragoza – Hosp. Metropolitano)\n"
            "♿ Estación con ascensor disponible\n"
            "🧍 Estás aquí (Origen seleccionado)\n"
            "🖱️ Clic izq: info/seleccionar · Clic der: cortar/abrir"
        )
        leyenda.setDefaultTextColor(QColor("#0F2C59"))
        leyenda.setFont(QFont("Segoe UI", 9, QFont.Bold))
        leyenda.setPos(325, 135)
        leyenda.setZValue(3)
        self.scene.addItem(leyenda)

    def _dibujar_estado_cortes(self):
        for item in self.items_cortes:
            self.scene.removeItem(item)
        self.items_cortes.clear()

        pen_corte = QPen(QColor("#DC2626"), 7, Qt.DashLine, Qt.RoundCap)
        for con in self.conexiones:
            est_o = self.estaciones.get(con["origen"])
            est_d = self.estaciones.get(con["destino"])
            if not est_o or not est_d:
                continue
            esta_cortada = con.get("cortada", False) or est_o.get("cortada", False) or est_d.get("cortada", False)
            if esta_cortada:
                x1, y1 = est_o["px"]
                x2, y2 = est_d["px"]
                linea = QGraphicsLineItem(x1, y1, x2, y2)
                linea.setPen(pen_corte)
                linea.setZValue(4)
                self.scene.addItem(linea)
                self.items_cortes.append(linea)

        self.actualizar_estilos_nodos()

    def actualizar_estilos_nodos(self):
        colores_linea = {
            1: QColor("#F59E0B"),
            2: QColor("#16A34A"),
            3: QColor("#EA580C"),
        }
        for est_id, nodo in self.nodos_graficos.items():
            info = self.estaciones[est_id]
            cortada = info.get("cortada", False)
            if cortada:
                nodo.setBrush(QBrush(QColor("#1E293B")))
                nodo.setPen(QPen(QColor("#EF4444"), 3))
            else:
                nodo.setBrush(QBrush(colores_linea.get(info["linea"], QColor("#0F172A"))))
                nodo.setPen(QPen(QColor("#FFFFFF"), 2))

    def _dibujar_nodos_y_nombres(self):
        coordenadas_etiquetadas = set()
        ascensor_por_px = {}
        for info in self.estaciones.values():
            px_key = tuple(info["px"])
            if info.get("ascensor", False):
                ascensor_por_px[px_key] = True

        for est_id, info in self.estaciones.items():
            x, y = info["px"]
            px_key = (x, y)
            es_transbordo = est_id in {
                "Cuauhtemoc_L1", "Cuauhtemoc_L2",
                "Zaragoza_L2", "Zaragoza_L3",
                "Felix_U_Gomez_L1", "Felix_U_Gomez_L3"
            }
            radio = 10 if es_transbordo else 8

            nodo = QGraphicsEllipseItem(x - radio, y - radio, radio * 2, radio * 2)
            nodo.setCursor(Qt.PointingHandCursor)
            nodo.setZValue(10)
            nodo.setData(0, est_id)
            self.scene.addItem(nodo)
            self.nodos_graficos[est_id] = nodo

            if px_key not in coordenadas_etiquetadas:
                coordenadas_etiquetadas.add(px_key)
                tiene_ascensor = ascensor_por_px.get(px_key, False)
                texto_nombre = info["nombre"].upper()
                if tiene_ascensor:
                    texto_nombre += " ♿"

                etiqueta = QGraphicsTextItem(texto_nombre)
                etiqueta.setDefaultTextColor(QColor("#0F2C59"))
                etiqueta.setFont(QFont("Segoe UI", 8, QFont.Bold))

                dx, dy, rot = AJUSTES_ETIQUETAS.get(est_id, (12, -10, 0))
                etiqueta.setPos(x + dx, y + dy)
                etiqueta.setRotation(rot)
                etiqueta.setZValue(9)
                self.scene.addItem(etiqueta)

        self.actualizar_estilos_nodos()

    # --- MONIGOTE "ESTÁS AQUÍ" EN LA ESTACIÓN DE ORIGEN ---
    def marcar_origen_monigote(self, est_id):
        for item in self.items_monigote:
            self.scene.removeItem(item)
        self.items_monigote.clear()

        if est_id not in self.estaciones:
            return

        x, y = self.estaciones[est_id]["px"]

        # Halo pulsante alrededor del origen
        halo = QGraphicsEllipseItem(x - 15, y - 15, 30, 30)
        halo.setBrush(QBrush(QColor(16, 185, 129, 70)))
        halo.setPen(QPen(QColor("#10B981"), 2.5))
        halo.setZValue(18)

        # Bocadillo "Estás aquí"
        texto = QGraphicsTextItem("🧍 Estás aquí")
        texto.setDefaultTextColor(QColor("#FFFFFF"))
        texto.setFont(QFont("Segoe UI", 8.5, QFont.Bold))
        rect_txt = texto.boundingRect()

        bx = x - rect_txt.width() / 2
        by = y - 46

        fondo_bocadillo = QGraphicsRectItem(bx - 6, by - 2, rect_txt.width() + 12, rect_txt.height() + 4)
        fondo_bocadillo.setBrush(QBrush(QColor("#0F2C59")))
        fondo_bocadillo.setPen(QPen(QColor("#10B981"), 2))
        fondo_bocadillo.setZValue(25)

        texto.setPos(bx, by)
        texto.setZValue(26)

        # Puntero triangular/línea hacia la bola
        puntero = QGraphicsLineItem(x, by + rect_txt.height() + 2, x, y - 10)
        puntero.setPen(QPen(QColor("#0F2C59"), 2.5))
        puntero.setZValue(24)

        self.scene.addItem(halo)
        self.scene.addItem(puntero)
        self.scene.addItem(fondo_bocadillo)
        self.scene.addItem(texto)
        self.items_monigote.extend([halo, puntero, fondo_bocadillo, texto])

    # --- TARJETA DE DESCRIPCIÓN AL PINCHAR EN UNA ESTACIÓN ---
    def mostrar_tarjeta_estacion(self, est_id):
        self.cerrar_tarjeta_estacion()
        if est_id not in self.estaciones:
            return

        info = self.estaciones[est_id]
        x, y = info["px"]

        # Comprobar si es estación de transbordo
        transbordos_info = []
        for t in self.datos_red.get("transbordos", []):
            if t["origen"] == est_id or t["destino"] == est_id:
                otro_id = t["destino"] if t["origen"] == est_id else t["origen"]
                linea_otro = self.estaciones[otro_id]["linea"]
                transbordos_info.append(f"Línea {linea_otro} ({t['longitud_m']} m)")

        estado_txt = "⛔ CORTADA (Fuera de servicio)" if info.get("cortada", False) else "✅ Operativa"
        tipo_txt = "Subterránea" if info["subterranea"] else "Elevada / Superficie"
        acc_txt = "Sí ♿ (Apta movilidad reducida)" if info["ascensor"] else f"No ({info['escaleras']} tramos escaleras)"
        trans_txt = f"\n🔄 Transbordo con: {', '.join(transbordos_info)}" if transbordos_info else ""

        descripcion = (
            f"📍 {info['nombre'].upper()} (Línea {info['linea']})\n"
            f"──────────────────────────\n"
            f"• Estado: {estado_txt}\n"
            f"• Tipo: {tipo_txt}\n"
            f"• Ascensor: {acc_txt}\n"
            f"• Capacidad / Aforo base: {info['aforo']} pas."
            f"{trans_txt}\n"
            f"• GPS: {info['lat']:.4f}, {info['lon']:.4f}"
        )

        texto_item = QGraphicsTextItem(descripcion)
        texto_item.setDefaultTextColor(QColor("#0F172A"))
        texto_item.setFont(QFont("Segoe UI", 8.5))
        rect = texto_item.boundingRect()

        # Colocar la tarjeta a la derecha de la estación (o a la izquierda si está muy pegada al borde derecho)
        px_card = x + 18 if x < 920 else x - rect.width() - 28
        py_card = max(135, min(y - 20, 720))

        caja = QGraphicsRectItem(px_card, py_card, rect.width() + 16, rect.height() + 12)
        caja.setBrush(QBrush(QColor("#FFFFFF")))
        caja.setPen(QPen(QColor("#2563EB"), 2))
        caja.setZValue(30)

        conector = QGraphicsLineItem(x, y, px_card if px_card > x else px_card + rect.width() + 16, py_card + 20)
        conector.setPen(QPen(QColor("#2563EB"), 1.5, Qt.DashLine))
        conector.setZValue(29)

        texto_item.setPos(px_card + 8, py_card + 6)
        texto_item.setZValue(31)

        self.scene.addItem(conector)
        self.scene.addItem(caja)
        self.scene.addItem(texto_item)
        self.items_popup_info.extend([conector, caja, texto_item])

    def cerrar_tarjeta_estacion(self):
        for item in self.items_popup_info:
            self.scene.removeItem(item)
        self.items_popup_info.clear()

    def _iniciar_simulacion_trenes(self):
        recorridos = {
            1: [
                "Talleres_L1", "San_Bernabe_L1", "Unidad_Modelo_L1", "Aztlan_L1",
                "Penitenciaria_L1", "Alfonso_Reyes_L1", "Mitras_L1", "Simon_Bolivar_L1",
                "Hospital_L1", "Edison_L1", "Central_L1", "Cuauhtemoc_L1",
                "Del_Golfo_L1", "Felix_U_Gomez_L1", "Parque_Fundidora_L1", "Y_Griega_L1",
                "Eloy_Cavazos_L1", "Lerdo_de_Tejeda_L1", "Exposicion_L1"
            ],
            2: [
                "Sendero_L2", "Santiago_Tapia_L2", "San_Nicolas_L2", "Anahuac_L2",
                "Universidad_L2", "Ninos_Heroes_L2", "Regina_L2", "Gral_Anaya_L2",
                "Cuauhtemoc_L2", "Alameda_L2", "Fundadores_L2", "Padre_Mier_L2",
                "Zaragoza_L2"
            ],
            3: [
                "Zaragoza_L3", "Santa_Lucia_L3", "Col_Obrera_L3",
                "Felix_U_Gomez_L3", "Metalurgicos_L3", "Col_Moderna_L3",
                "Ruiz_Cortines_L3", "Los_Angeles_L3", "Hospital_Metropolitano_L3"
            ]
        }

        colores_tren = {
            1: QColor("#D97706"),
            2: QColor("#15803D"),
            3: QColor("#DC2626"),
        }

        config_trenes = [
            (1, 1, 0.2, 1), (1, 6, 0.7, -1), (1, 16, 0.5, -1),
            (2, 1, 0.3, 1), (2, 6, 0.6, -1), (2, 10, 0.2, 1),
            (3, 1, 0.4, 1), (3, 6, 0.5, -1),
        ]

        for linea, idx_ini, prog_ini, sentido in config_trenes:
            punto = QGraphicsEllipseItem(-6, -6, 12, 12)
            punto.setBrush(QBrush(colores_tren[linea]))
            punto.setPen(QPen(QColor("#0F172A"), 2))
            punto.setZValue(20)
            self.scene.addItem(punto)

            tren = TrenAnimado(linea, recorridos[linea], idx_ini, prog_ini, sentido, punto)
            self.trenes.append(tren)

        self._posicionar_trenes()

        self.timer_trenes = QTimer(self)
        self.timer_trenes.timeout.connect(self._actualizar_trenes)
        self.timer_trenes.start(int(DT_FRAME_SEG * 1000))

    def set_servicio_activo(self, activo):
        self.servicio_activo = activo
        for tren in self.trenes:
            tren.item.setVisible(activo)

    def _actualizar_trenes(self):
        if not self.servicio_activo:
            return

        for tren in self.trenes:
            max_idx = len(tren.recorrido_ids) - 1

            if tren.estado == "parado":
                tren.tiempo_espera_restante -= DT_FRAME_SEG
                if tren.tiempo_espera_restante <= 0:
                    tren.estado = "viajando"
                    tren.tiempo_espera_restante = 0.0
                    if tren.idx_estacion >= max_idx:
                        tren.sentido = -1
                    elif tren.idx_estacion <= 0:
                        tren.sentido = 1
                continue

            tren.progreso_tramo += DT_FRAME_SEG / TIEMPO_TRAMO_SEG

            if tren.progreso_tramo >= 1.0:
                tren.idx_estacion = max(0, min(max_idx, tren.idx_estacion + tren.sentido))
                tren.progreso_tramo = 0.0
                tren.estado = "parado"
                tren.tiempo_espera_restante = TIEMPO_PARADA_SEG

        self._posicionar_trenes()

    def _posicionar_trenes(self):
        for tren in self.trenes:
            max_idx = len(tren.recorrido_ids) - 1
            id_a = tren.recorrido_ids[tren.idx_estacion]
            est_a = self.estaciones.get(id_a)

            if not est_a:
                continue

            if tren.estado == "parado" or tren.progreso_tramo == 0.0:
                tren.item.setPos(*est_a["px"])
                continue

            idx_sig = max(0, min(max_idx, tren.idx_estacion + tren.sentido))
            id_b = tren.recorrido_ids[idx_sig]
            est_b = self.estaciones.get(id_b)

            if est_b:
                x1, y1 = est_a["px"]
                x2, y2 = est_b["px"]
                x = x1 + (x2 - x1) * tren.progreso_tramo
                y = y1 + (y2 - y1) * tren.progreso_tramo
                tren.item.setPos(x, y)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsEllipseItem) and item.data(0):
            est_id = item.data(0)
            if event.button() == Qt.LeftButton:
                self.mostrar_tarjeta_estacion(est_id)
                self.estacion_clicada.emit(est_id)
            elif event.button() == Qt.RightButton:
                self.estacion_toggle_corte.emit(est_id)
                self.mostrar_tarjeta_estacion(est_id)
        else:
            # Si pincha en el fondo vacío del mapa, cerramos la ficha flotante
            if event.button() == Qt.LeftButton:
                self.cerrar_tarjeta_estacion()
        super().mousePressEvent(event)

    def dibujar_ruta(self, lista_ids_estaciones):
        self.limpiar_ruta()
        if not lista_ids_estaciones or len(lista_ids_estaciones) < 2:
            return

        pen_borde = QPen(QColor("#0F2C59"), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        pen_centro = QPen(QColor("#38BDF8"), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        for i in range(len(lista_ids_estaciones) - 1):
            id_a = lista_ids_estaciones[i]
            id_b = lista_ids_estaciones[i + 1]
            if id_a in self.estaciones and id_b in self.estaciones:
                x1, y1 = self.estaciones[id_a]["px"]
                x2, y2 = self.estaciones[id_b]["px"]
                if (x1, y1) == (x2, y2):
                    continue

                linea_ext = QGraphicsLineItem(x1, y1, x2, y2)
                linea_ext.setPen(pen_borde)
                linea_ext.setZValue(5)

                linea_int = QGraphicsLineItem(x1, y1, x2, y2)
                linea_int.setPen(pen_centro)
                linea_int.setZValue(6)

                self.scene.addItem(linea_ext)
                self.scene.addItem(linea_int)
                self.items_ruta.extend([linea_ext, linea_int])

        # Destino en rojo intenso (el origen ya tiene el monigote "Estás aquí")
        dest_id = lista_ids_estaciones[-1]
        if dest_id in self.estaciones:
            x, y = self.estaciones[dest_id]["px"]
            marcador = QGraphicsEllipseItem(x - 12, y - 12, 24, 24)
            marcador.setBrush(QBrush(QColor("#EF4444")))
            marcador.setPen(QPen(QColor("#FFFFFF"), 3))
            marcador.setZValue(15)
            self.scene.addItem(marcador)
            self.items_ruta.append(marcador)

    def limpiar_ruta(self):
        for item in self.items_ruta:
            self.scene.removeItem(item)
        self.items_ruta.clear()