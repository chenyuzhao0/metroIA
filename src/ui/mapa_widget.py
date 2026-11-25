import os
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtCore import Qt, Signal

class MapaMetrorreyView(QGraphicsView):
    # Señal que avisa a la ventana principal cuando el usuario hace clic en una estación
    estacion_clicada = Signal(str)

    def __init__(self, estaciones_coords, ruta_imagen="assets/plano_metrorrey.png"):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.estaciones_coords = estaciones_coords  # Diccionario: {"Nombre": (x, y, linea)}
        self.items_ruta = []
        self.nodos_graficos = {}

        # Renderizado suave y navegación tipo mapa (arrastrar con ratón y zoom al cursor)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setStyleSheet("border: 1px solid #CBD5E1; border-radius: 8px; background-color: #EAE5DC;")

        self._cargar_fondo(ruta_imagen)
        self._dibujar_nodos_interactivos()

    def _cargar_fondo(self, ruta_imagen):
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            self.scene.addPixmap(pixmap)
            self.setSceneRect(pixmap.rect())
        else:
            # Tamaño base proporcional al plano si aún no se ha guardado la imagen
            self.setSceneRect(0, 0, 1280, 780)
            aviso = QGraphicsTextItem("Guarda el plano en 'assets/plano_metrorrey.png' para verlo de fondo")
            aviso.setDefaultTextColor(QColor("#64748B"))
            aviso.setPos(380, 20)
            self.scene.addItem(aviso)

    def _dibujar_nodos_interactivos(self):
        colores_linea = {
            1: QColor("#F59E0B"),  # Línea 1 - Amarillo
            2: QColor("#16A34A"),  # Línea 2 - Verde
            3: QColor("#EA580C"),  # Línea 3 - Rojo/Naranja
        }
        for nombre, (x, y, linea) in self.estaciones_coords.items():
            radio = 8
            nodo = QGraphicsEllipseItem(x - radio, y - radio, radio * 2, radio * 2)
            nodo.setBrush(QBrush(colores_linea.get(linea, QColor("#0F172A"))))
            nodo.setPen(QPen(QColor("#FFFFFF"), 2))
            nodo.setToolTip(f"{nombre} (Línea {linea}) — Clic para seleccionar")
            nodo.setCursor(Qt.PointingHandCursor)
            nodo.setZValue(10)
            nodo.setData(0, nombre)
            self.scene.addItem(nodo)
            self.nodos_graficos[nombre] = nodo

    def wheelEvent(self, event):
        """Zoom fluido con la rueda del ratón."""
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsEllipseItem) and item.data(0):
                self.estacion_clicada.emit(item.data(0))
        super().mousePressEvent(event)

    def dibujar_ruta(self, lista_estaciones):
        """Resalta sobre el mapa el camino óptimo devuelto por A*."""
        self.limpiar_ruta()
        if not lista_estaciones or len(lista_estaciones) < 2:
            return

        # Dibujar tramos iluminados
        pen_borde = QPen(QColor("#0F2C59"), 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        pen_centro = QPen(QColor("#38BDF8"), 5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        for i in range(len(lista_estaciones) - 1):
            est_a = lista_estaciones[i]
            est_b = lista_estaciones[i + 1]
            if est_a in self.estaciones_coords and est_b in self.estaciones_coords:
                x1, y1, _ = self.estaciones_coords[est_a]
                x2, y2, _ = self.estaciones_coords[est_b]

                linea_ext = QGraphicsLineItem(x1, y1, x2, y2)
                linea_ext.setPen(pen_borde)
                linea_ext.setZValue(5)

                linea_int = QGraphicsLineItem(x1, y1, x2, y2)
                linea_int.setPen(pen_centro)
                linea_int.setZValue(6)

                self.scene.addItem(linea_ext)
                self.scene.addItem(linea_int)
                self.items_ruta.extend([linea_ext, linea_int])

        # Marcar origen (verde brillante) y destino (rojo intenso)
        for idx, est in enumerate([lista_estaciones[0], lista_estaciones[-1]]):
            if est in self.estaciones_coords:
                x, y, _ = self.estaciones_coords[est]
                color = QColor("#10B981") if idx == 0 else QColor("#EF4444")
                marcador = QGraphicsEllipseItem(x - 12, y - 12, 24, 24)
                marcador.setBrush(QBrush(color))
                marcador.setPen(QPen(QColor("#FFFFFF"), 3))
                marcador.setZValue(15)
                self.scene.addItem(marcador)
                self.items_ruta.append(marcador)

    def limpiar_ruta(self):
        for item in self.items_ruta:
            self.scene.removeItem(item)
        self.items_ruta.clear()