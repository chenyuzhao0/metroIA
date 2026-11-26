import os
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsRectItem, QGraphicsPolygonItem
)
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont, QPolygonF
from PySide6.QtCore import Qt, Signal, QTimer, QPointF

TIEMPO_TRAMO_SEG = 180.0   # 3 minutos entre estaciones
TIEMPO_PARADA_SEG = 30.0   # 30 segundos en cada estación
DT_FRAME_SEG = 0.05

AJUSTES_ETIQUETAS = {
    # Línea 1
    "Talleres_L1": (16, -11, 0),
    "San_Bernabe_L1": (16, -11, 0),
    "Unidad_Modelo_L1": (16, -11, 0),
    "Aztlan_L1": (16, -11, 0),
    "Penitenciaria_L1": (-115, -11, 0),
    "Alfonso_Reyes_L1": (-118, -11, 0),
    "Mitras_L1": (-66, -11, 0),
    "Simon_Bolivar_L1": (-120, -11, 0),
    "Hospital_L1": (-78, -11, 0),
    "Edison_L1": (-9, 16, 90),
    "Central_L1": (-9, 16, 90),
    "Cuauhtemoc_L1": (-56, -34, 0),
    "Del_Golfo_L1": (-30, -30, 0),
    "Felix_U_Gomez_L1": (16, -24, 0),
    "Parque_Fundidora_L1": (-9, 16, 90),
    "Y_Griega_L1": (-9, 16, 90),
    "Eloy_Cavazos_L1": (-9, 16, 90),
    "Lerdo_de_Tejeda_L1": (-9, 16, 90),
    "Exposicion_L1": (-9, 16, 90),

    # Línea 2
    "Sendero_L2": (-80, -11, 0),
    "Santiago_Tapia_L2": (-118, -11, 0),
    "San_Nicolas_L2": (-102, -11, 0),
    "Anahuac_L2": (-82, -11, 0),
    "Universidad_L2": (-100, -11, 0),
    "Ninos_Heroes_L2": (-112, -11, 0),
    "Regina_L2": (-68, -11, 0),
    "Gral_Anaya_L2": (-98, -11, 0),
    "Alameda_L2": (16, -11, 0),
    "Fundadores_L2": (-100, -11, 0),
    "Padre_Mier_L2": (-9, 16, 90),
    "Zaragoza_L2": (-9, 16, 90),

    # Línea 3
    "Santa_Lucia_L3": (-9, 16, 90),
    "Col_Obrera_L3": (-100, -11, 0),
    "Metalurgicos_L3": (16, -11, 0),
    "Col_Moderna_L3": (16, -11, 0),
    "Ruiz_Cortines_L3": (16, -11, 0),
    "Los_Angeles_L3": (16, -11, 0),
    "Hospital_Metropolitano_L3": (16, -14, 0),
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
    estacion_clicada = Signal(str)
    estacion_toggle_corte = Signal(str)

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
        self.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 12px; background-color: #EBE6DD;")

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
            # Lienzo amplio para que no se corte ni Padre Mier abajo ni el monigote arriba
            self.setSceneRect(220, 110, 1020, 810)
            self._dibujar_decoracion_plano()
            self._dibujar_lineas_base()
            self._dibujar_tarjeta_simbologia()

    def _dibujar_decoracion_plano(self):
        """Dibuja elementos arquitectónicos del plano oficial: retícula sutil, cabecera Metrorrey y rosa de los vientos."""
        # Retícula suave de fondo tipo plano urbano
        pen_grid = QPen(QColor(214, 208, 196, 130), 1)
        for gx in range(240, 1240, 80):
            l = QGraphicsLineItem(gx, 110, gx, 920)
            l.setPen(pen_grid)
            l.setZValue(0)
            self.scene.addItem(l)
        for gy in range(130, 920, 80):
            l = QGraphicsLineItem(220, gy, 1240, gy)
            l.setPen(pen_grid)
            l.setZValue(0)
            self.scene.addItem(l)

        # Emblema superior derecho estilo Metrorrey
        badge_bg = QGraphicsRectItem(995, 135, 215, 62)
        badge_bg.setBrush(QBrush(QColor("#FFFFFF")))
        badge_bg.setPen(QPen(QColor("#0F2C59"), 2.5))
        badge_bg.setZValue(2)
        self.scene.addItem(badge_bg)

        logo_m = QGraphicsTextItem("m")
        logo_m.setDefaultTextColor(QColor("#E11D48"))
        logo_m.setFont(QFont("Arial Black", 26, QFont.Black))
        logo_m.setPos(1006, 133)
        logo_m.setZValue(3)
        self.scene.addItem(logo_m)

        logo_txt = QGraphicsTextItem("METRORREY\nRed Metro · L1 · L2 · L3")
        logo_txt.setDefaultTextColor(QColor("#0F2C59"))
        logo_txt.setFont(QFont("Segoe UI", 9, QFont.Bold))
        logo_txt.setPos(1056, 145)
        logo_txt.setZValue(3)
        self.scene.addItem(logo_txt)

        # Rosa de los vientos (Norte) en la parte inferior central-izquierda
        nx, ny = 490, 795
        aguja_norte = QPolygonF([QPointF(nx, ny - 26), QPointF(nx - 8, ny), QPointF(nx + 8, ny)])
        poly_n = QGraphicsPolygonItem(aguja_norte)
        poly_n.setBrush(QBrush(QColor("#DC2626")))
        poly_n.setPen(QPen(Qt.NoPen))
        poly_n.setZValue(2)
        self.scene.addItem(poly_n)

        aguja_sur = QPolygonF([QPointF(nx, ny + 26), QPointF(nx - 8, ny), QPointF(nx + 8, ny)])
        poly_s = QGraphicsPolygonItem(aguja_sur)
        poly_s.setBrush(QBrush(QColor("#94A3B8")))
        poly_s.setPen(QPen(Qt.NoPen))
        poly_s.setZValue(2)
        self.scene.addItem(poly_s)

        lbl_n = QGraphicsTextItem("N")
        lbl_n.setDefaultTextColor(QColor("#0F2C59"))
        lbl_n.setFont(QFont("Segoe UI", 11, QFont.Black))
        lbl_n.setPos(nx - 9, ny + 24)
        lbl_n.setZValue(2)
        self.scene.addItem(lbl_n)

    def _dibujar_lineas_base(self):
        """Dibuja las vías con contorno sutil y trazo limpio."""
        colores_linea = {
            1: QColor("#F59E0B"),  # Línea 1 - Amarillo
            2: QColor("#16A34A"),  # Línea 2 - Verde
            3: QColor("#EA580C"),  # Línea 3 - Rojo/Naranja
        }
        for con in self.conexiones:
            est_o = self.estaciones.get(con["origen"])
            est_d = self.estaciones.get(con["destino"])
            if not est_o or not est_d:
                continue
            x1, y1 = est_o["px"]
            x2, y2 = est_d["px"]
            color = colores_linea.get(est_o["linea"], QColor("#64748B"))

            # Sombra/borde blanco para que la vía destaque sobre el fondo
            sombra_via = QGraphicsLineItem(x1, y1, x2, y2)
            sombra_via.setPen(QPen(QColor("#FFFFFF"), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            sombra_via.setZValue(1)
            self.scene.addItem(sombra_via)

            tramo = QGraphicsLineItem(x1, y1, x2, y2)
            tramo.setPen(QPen(color, 6.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            tramo.setZValue(2)
            self.scene.addItem(tramo)

    def _dibujar_tarjeta_simbologia(self):
        """Tarjeta oficial de simbología en la esquina inferior izquierda (sin estorbar a Talleres)."""
        sx, sy = 240, 625
        ancho, alto = 215, 245

        caja = QGraphicsRectItem(sx, sy, ancho, alto)
        caja.setBrush(QBrush(QColor("#FFFFFF")))
        caja.setPen(QPen(QColor("#0F2C59"), 2))
        caja.setZValue(2)
        self.scene.addItem(caja)

        cabecera = QGraphicsRectItem(sx, sy, ancho, 28)
        cabecera.setBrush(QBrush(QColor("#0F2C59")))
        cabecera.setPen(QPen(Qt.NoPen))
        cabecera.setZValue(3)
        self.scene.addItem(cabecera)

        tit = QGraphicsTextItem("SIMBOLOGÍA")
        tit.setDefaultTextColor(QColor("#FFFFFF"))
        tit.setFont(QFont("Segoe UI", 9, QFont.Bold))
        tit.setPos(sx + 62, sy + 3)
        tit.setZValue(4)
        self.scene.addItem(tit)

        items_leyenda = [
            ("#F59E0B", "Línea 1 (Talleres – Exposición)"),
            ("#16A34A", "Línea 2 (Sendero – Zaragoza)"),
            ("#EA580C", "Línea 3 (Zaragoza – H. Metrop.)"),
        ]
        y_curr = sy + 38
        for hex_col, nombre_l in items_leyenda:
            linea_muestra = QGraphicsLineItem(sx + 12, y_curr + 9, sx + 32, y_curr + 9)
            linea_muestra.setPen(QPen(QColor(hex_col), 5, Qt.SolidLine, Qt.RoundCap))
            linea_muestra.setZValue(4)
            self.scene.addItem(linea_muestra)

            txt = QGraphicsTextItem(nombre_l)
            txt.setDefaultTextColor(QColor("#1E293B"))
            txt.setFont(QFont("Segoe UI", 8, QFont.Bold))
            txt.setPos(sx + 38, y_curr - 1)
            txt.setZValue(4)
            self.scene.addItem(txt)
            y_curr += 24

        notas = QGraphicsTextItem(
            "◎  Estación de transbordo\n"
            "♿  Ascensor disponible\n"
            "🧍  Estación de origen actual\n"
            "⛔  Tramo/estación cortada\n"
            "────────────────────\n"
            "🖱️ Clic izq: ficha / elegir\n"
            "🖱️ Clic der: cortar / abrir"
        )
        notas.setDefaultTextColor(QColor("#334155"))
        notas.setFont(QFont("Segoe UI", 8))
        notas.setPos(sx + 10, y_curr + 2)
        notas.setZValue(4)
        self.scene.addItem(notas)

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
        transbordos_ids = {
            "Cuauhtemoc_L1", "Cuauhtemoc_L2",
            "Zaragoza_L2", "Zaragoza_L3",
            "Felix_U_Gomez_L1", "Felix_U_Gomez_L3"
        }
        for est_id, nodo in self.nodos_graficos.items():
            info = self.estaciones[est_id]
            cortada = info.get("cortada", False)
            if cortada:
                nodo.setBrush(QBrush(QColor("#1E293B")))
                nodo.setPen(QPen(QColor("#EF4444"), 3))
            elif est_id in transbordos_ids:
                # Estaciones de transbordo con anillo blanco interior y borde azul marino
                nodo.setBrush(QBrush(QColor("#FFFFFF")))
                nodo.setPen(QPen(QColor("#0F2C59"), 3.5))
            else:
                nodo.setBrush(QBrush(colores_linea.get(info["linea"], QColor("#0F172A"))))
                nodo.setPen(QPen(QColor("#FFFFFF"), 2.2))

    def _dibujar_nodos_y_nombres(self):
        coordenadas_etiquetadas = set()
        ascensor_por_px = {}
        for info in self.estaciones.values():
            px_key = tuple(info["px"])
            if info.get("ascensor", False):
                ascensor_por_px[px_key] = True

        transbordos_ids = {
            "Cuauhtemoc_L1", "Cuauhtemoc_L2",
            "Zaragoza_L2", "Zaragoza_L3",
            "Felix_U_Gomez_L1", "Felix_U_Gomez_L3"
        }

        for est_id, info in self.estaciones.items():
            x, y = info["px"]
            px_key = (x, y)
            es_transbordo = est_id in transbordos_ids
            radio = 11 if es_transbordo else 8

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

                dx, dy, rot = AJUSTES_ETIQUETAS.get(est_id, (14, -11, 0))
                etiqueta.setPos(x + dx, y + dy)
                etiqueta.setRotation(rot)
                etiqueta.setZValue(9)
                self.scene.addItem(etiqueta)

        self.actualizar_estilos_nodos()

    def marcar_origen_monigote(self, est_id):
        for item in self.items_monigote:
            self.scene.removeItem(item)
        self.items_monigote.clear()

        if est_id not in self.estaciones:
            return

        x, y = self.estaciones[est_id]["px"]

        halo = QGraphicsEllipseItem(x - 16, y - 16, 32, 32)
        halo.setBrush(QBrush(QColor(16, 185, 129, 75)))
        halo.setPen(QPen(QColor("#10B981"), 2.5))
        halo.setZValue(18)

        texto = QGraphicsTextItem("🧍 Estás aquí")
        texto.setDefaultTextColor(QColor("#FFFFFF"))
        texto.setFont(QFont("Segoe UI", 8.5, QFont.Bold))
        rect_txt = texto.boundingRect()

        bx = x - rect_txt.width() / 2
        by = y - 48

        fondo_bocadillo = QGraphicsRectItem(bx - 6, by - 2, rect_txt.width() + 12, rect_txt.height() + 4)
        fondo_bocadillo.setBrush(QBrush(QColor("#0F2C59")))
        fondo_bocadillo.setPen(QPen(QColor("#10B981"), 2))
        fondo_bocadillo.setZValue(25)

        texto.setPos(bx, by)
        texto.setZValue(26)

        puntero = QGraphicsLineItem(x, by + rect_txt.height() + 2, x, y - 11)
        puntero.setPen(QPen(QColor("#0F2C59"), 2.5))
        puntero.setZValue(24)

        self.scene.addItem(halo)
        self.scene.addItem(puntero)
        self.scene.addItem(fondo_bocadillo)
        self.scene.addItem(texto)
        self.items_monigote.extend([halo, puntero, fondo_bocadillo, texto])

    def mostrar_tarjeta_estacion(self, est_id):
        self.cerrar_tarjeta_estacion()
        if est_id not in self.estaciones:
            return

        info = self.estaciones[est_id]
        x, y = info["px"]

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

        px_card = x + 18 if x < 920 else x - rect.width() - 28
        py_card = max(135, min(y - 20, 740))

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
            if event.button() == Qt.LeftButton:
                self.cerrar_tarjeta_estacion()
        super().mousePressEvent(event)

    def dibujar_ruta(self, lista_ids_estaciones):
        self.limpiar_ruta()
        if not lista_ids_estaciones or len(lista_ids_estaciones) < 2:
            return

        pen_halo = QPen(QColor(56, 189, 248, 95), 16, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
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

                linea_halo = QGraphicsLineItem(x1, y1, x2, y2)
                linea_halo.setPen(pen_halo)
                linea_halo.setZValue(4.5)

                linea_ext = QGraphicsLineItem(x1, y1, x2, y2)
                linea_ext.setPen(pen_borde)
                linea_ext.setZValue(5)

                linea_int = QGraphicsLineItem(x1, y1, x2, y2)
                linea_int.setPen(pen_centro)
                linea_int.setZValue(6)

                self.scene.addItem(linea_halo)
                self.scene.addItem(linea_ext)
                self.scene.addItem(linea_int)
                self.items_ruta.extend([linea_halo, linea_ext, linea_int])

        dest_id = lista_ids_estaciones[-1]
        if dest_id in self.estaciones:
            x, y = self.estaciones[dest_id]["px"]
            marcador = QGraphicsEllipseItem(x - 13, y - 13, 26, 26)
            marcador.setBrush(QBrush(QColor("#EF4444")))
            marcador.setPen(QPen(QColor("#FFFFFF"), 3))
            marcador.setZValue(15)
            self.scene.addItem(marcador)
            self.items_ruta.append(marcador)

    def limpiar_ruta(self):
        for item in self.items_ruta:
            self.scene.removeItem(item)
        self.items_ruta.clear()