from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QGroupBox, QListWidget, QFrame, QSlider
)
from PySide6.QtCore import Qt
from src.ui.mapa_widget import MapaMetrorreyView

# Coordenadas aproximadas (en píxeles sobre el plano 1280x780) de las 3 líneas y sus transbordos
ESTACIONES_METRORREY = {
    # LÍNEA 1 (Amarillo: Talleres -> Exposición)
    "Talleres": (381, 270, 1),
    "San Bernabé": (419, 309, 1),
    "Unidad Modelo": (456, 344, 1),
    "Aztlán": (490, 377, 1),
    "Penitenciaría": (555, 429, 1),
    "Alfonso Reyes": (555, 474, 1),
    "Mitras": (555, 519, 1),
    "Simón Bolívar": (555, 565, 1),
    "Hospital": (555, 623, 1),
    "Edison": (597, 623, 1),
    "Central": (646, 623, 1),
    "Cuauhtémoc": (693, 627, 1),      # Transbordo L1 - L2
    "Del Golfo": (753, 643, 1),
    "Félix U. Gómez": (814, 656, 1),  # Transbordo L1 - L3
    "Parque Fundidora": (871, 684, 1),
    "Y Griega": (929, 697, 1),
    "Eloy Cavazos": (985, 709, 1),
    "Lerdo de Tejada": (1040, 718, 1),
    "Exposición": (1093, 725, 1),

    # LÍNEA 2 (Verde: Sendero -> General Ignacio Zaragoza)
    "Sendero": (804, 179, 2),
    "Santiago Tapia": (796, 232, 2),
    "San Nicolás": (786, 286, 2),
    "Anáhuac": (764, 353, 2),
    "Universidad": (752, 405, 2),
    "Niños Héroes": (738, 464, 2),
    "Regina": (726, 518, 2),
    "General Anaya": (707, 571, 2),
    # Cuauhtémoc ya incluida (transbordo)
    "Alameda": (693, 682, 2),
    "Fundadores": (682, 731, 2),
    "Padre Mier": (701, 773, 2),
    "General Ignacio Zaragoza": (739, 773, 2),  # Transbordo L2 - L3

    # LÍNEA 3 (Rojo: General Ignacio Zaragoza -> Hospital Metropolitano)
    "Santa Lucía": (783, 753, 3),
    "Colonia Obrera": (802, 705, 3),
    # Félix U. Gómez ya incluida (transbordo)
    "Metalúrgicos": (828, 608, 3),
    "Colonia Moderna": (844, 560, 3),
    "Ruiz Cortines": (882, 521, 3),
    "Los Ángeles": (920, 490, 3),
    "Hospital Metropolitano": (952, 458, 3),
}


class MainWindow(QMainWindow):
    def __init__(self, callback_calcular_ruta=None):
        super().__init__()
        self.callback_calcular_ruta = callback_calcular_ruta
        self.turno_clic_origen = True

        self.setWindowTitle("Metrorrey A* — Planificador de Trayecto Óptimo (Líneas 1, 2 y 3)")
        self.resize(1380, 820)
        self._aplicar_estilos()
        self._construir_interfaz()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
            }
            QLabel#TituloApp {
                font-size: 20px;
                font-weight: bold;
                color: #0F2C59;
            }
            QLabel#SubtituloApp {
                font-size: 12px;
                color: #475569;
            }
            QGroupBox {
                font-weight: bold;
                color: #0F2C59;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 12px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox {
                padding: 6px 10px;
                border: 1px solid #94A3B8;
                border-radius: 6px;
                background-color: #FFFFFF;
                font-size: 13px;
            }
            QPushButton#BtnCalcular {
                background-color: #0F2C59;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton#BtnCalcular:hover {
                background-color: #1E40AF;
            }
            QPushButton#BtnLimpiar {
                background-color: #E2E8F0;
                color: #334155;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton#BtnLimpiar:hover {
                background-color: #CBD5E1;
            }
            QListWidget {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: #F8FAFC;
                font-size: 13px;
                padding: 4px;
            }
        """)

    def _construir_interfaz(self):
        contenedor = QWidget()
        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(14, 14, 14, 14)
        layout_principal.setSpacing(14)

        # --- PANEL IZQUIERDO: CONTROLES Y PARÁMETROS A* ---
        panel_control = QFrame()
        panel_control.setFixedWidth(380)
        layout_izq = QVBoxLayout(panel_control)
        layout_izq.setContentsMargins(0, 0, 0, 0)
        layout_izq.setSpacing(10)

        # Encabezado institucional Metrorrey
        lbl_titulo = QLabel("METRORREY · Ruta Óptima A*")
        lbl_titulo.setObjectName("TituloApp")
        lbl_subtitulo = QLabel("Líneas 1, 2 y 3 · Haz clic en el mapa o usa los selectores")
        lbl_subtitulo.setObjectName("SubtituloApp")
        layout_izq.addWidget(lbl_titulo)
        layout_izq.addWidget(lbl_subtitulo)

        # Grupo 1: Selección de Origen y Destino
        grupo_trayecto = QGroupBox("1. Selección de Estaciones")
        layout_trayecto = QVBoxLayout(grupo_trayecto)

        estaciones_ordenadas = sorted(ESTACIONES_METRORREY.keys())

        layout_trayecto.addWidget(QLabel("Estación de Origen:"))
        self.combo_origen = QComboBox()
        self.combo_origen.addItems(estaciones_ordenadas)
        self.combo_origen.setCurrentText("Talleres")
        layout_trayecto.addWidget(self.combo_origen)

        layout_trayecto.addWidget(QLabel("Estación de Destino:"))
        self.combo_destino = QComboBox()
        self.combo_destino.addItems(estaciones_ordenadas)
        self.combo_destino.setCurrentText("Hospital Metropolitano")
        layout_trayecto.addWidget(self.combo_destino)

        btn_invertir = QPushButton("⇅ Invertir Origen / Destino")
        btn_invertir.clicked.connect(self._invertir_estaciones)
        layout_trayecto.addWidget(btn_invertir)

        layout_izq.addWidget(grupo_trayecto)

        # Grupo 2: Circunstancias / Factores para g(n) en A*
        grupo_factores = QGroupBox("2. Criterios y Circunstancias (Coste g(n))")
        layout_factores = QVBoxLayout(grupo_factores)

        self.chk_movilidad_reducida = QCheckBox("Movilidad reducida (penalizar escaleras/subterráneas)")
        self.chk_hora_punta = QCheckBox("Hora punta (mayor tiempo de espera en transbordos)")
        self.chk_lluvia = QCheckBox("Clima adverso / Lluvia (velocidad reducida en tramos elevados)")
        self.chk_evitar_transbordos = QCheckBox("Priorizar mínimo número de transbordos")

        layout_factores.addWidget(self.chk_movilidad_reducida)
        layout_factores.addWidget(self.chk_hora_punta)
        layout_factores.addWidget(self.chk_lluvia)
        layout_factores.addWidget(self.chk_evitar_transbordos)

        self.lbl_penalizacion = QLabel("Penalización extra por transbordo: 5 min")
        self.slider_transbordo = QSlider(Qt.Horizontal)
        self.slider_transbordo.setRange(1, 15)
        self.slider_transbordo.setValue(5)
        self.slider_transbordo.valueChanged.connect(
            lambda v: self.lbl_penalizacion.setText(f"Penalización extra por transbordo: {v} min")
        )
        layout_factores.addWidget(self.lbl_penalizacion)
        layout_factores.addWidget(self.slider_transbordo)

        layout_izq.addWidget(grupo_factores)

        # Botones de acción
        layout_botones = QHBoxLayout()
        self.btn_calcular = QPushButton("Calcular Ruta Óptima (A*)")
        self.btn_calcular.setObjectName("BtnCalcular")
        self.btn_calcular.clicked.connect(self._ejecutar_calculo)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("BtnLimpiar")
        self.btn_limpiar.clicked.connect(self._limpiar_todo)

        layout_botones.addWidget(self.btn_calcular, 3)
        layout_botones.addWidget(self.btn_limpiar, 1)
        layout_izq.addLayout(layout_botones)

        # Grupo 3: Resultados e Itinerario
        grupo_resultados = QGroupBox("3. Resultado del Algoritmo A*")
        layout_res = QVBoxLayout(grupo_resultados)

        self.lbl_resumen = QLabel("Tiempo estimado: — | Estaciones: — | Transbordos: —")
        self.lbl_resumen.setStyleSheet("font-weight: bold; color: #0F2C59;")
        layout_res.addWidget(self.lbl_resumen)

        self.lista_pasos = QListWidget()
        layout_res.addWidget(self.lista_pasos)

        layout_izq.addWidget(grupo_resultados, 1)

        # --- PANEL DERECHO: PLANO INTERACTIVO ---
        self.mapa_view = MapaMetrorreyView(ESTACIONES_METRORREY)
        self.mapa_view.estacion_clicada.connect(self._al_clicar_estacion_en_mapa)

        layout_principal.addWidget(panel_control)
        layout_principal.addWidget(self.mapa_view, 1)
        self.setCentralWidget(contenedor)

    def _invertir_estaciones(self):
        origen = self.combo_origen.currentText()
        destino = self.combo_destino.currentText()
        self.combo_origen.setCurrentText(destino)
        self.combo_destino.setCurrentText(origen)

    def _al_clicar_estacion_en_mapa(self, nombre_estacion):
        if self.turno_clic_origen:
            self.combo_origen.setCurrentText(nombre_estacion)
        else:
            self.combo_destino.setCurrentText(nombre_estacion)
        self.turno_clic_origen = not self.turno_clic_origen

    def _limpiar_todo(self):
        self.mapa_view.limpiar_ruta()
        self.lista_pasos.clear()
        self.lbl_resumen.setText("Tiempo estimado: — | Estaciones: — | Transbordos: —")

    def _ejecutar_calculo(self):
        origen = self.combo_origen.currentText()
        destino = self.combo_destino.currentText()

        parametros = {
            "origen": origen,
            "destino": destino,
            "movilidad_reducida": self.chk_movilidad_reducida.isChecked(),
            "hora_punta": self.chk_hora_punta.isChecked(),
            "lluvia": self.chk_lluvia.isChecked(),
            "evitar_transbordos": self.chk_evitar_transbordos.isChecked(),
            "penalizacion_transbordo": self.slider_transbordo.value(),
        }

        if self.callback_calcular_ruta:
            # Aquí se conecta vuestro algoritmo A* de src/algorithm/
            resultado = self.callback_calcular_ruta(parametros)
            self.mostrar_resultado(
                ruta=resultado["ruta"],
                tiempo_total=resultado["tiempo_total"],
                transbordos=resultado["transbordos"],
                coste_g=resultado.get("coste_g", 0)
            )
        else:
            # Demostración visual de ejemplo (Talleres -> Cuauhtémoc -> Félix U. Gómez -> Hospital Metropolitano)
            ruta_demo = [
                "Talleres", "San Bernabé", "Unidad Modelo", "Aztlán",
                "Penitenciaría", "Alfonso Reyes", "Mitras", "Simón Bolívar",
                "Hospital", "Edison", "Central", "Cuauhtémoc",
                "Del Golfo", "Félix U. Gómez", "Metalúrgicos",
                "Colonia Moderna", "Ruiz Cortines", "Los Ángeles", "Hospital Metropolitano"
            ]
            self.mostrar_resultado(ruta_demo, tiempo_total=34.5, transbordos=["Félix U. Gómez (L1 → L3)"], coste_g=34.5)

    def mostrar_resultado(self, ruta, tiempo_total, transbordos, coste_g):
        self.mapa_view.dibujar_ruta(ruta)
        self.lista_pasos.clear()

        num_transbordos = len(transbordos)
        self.lbl_resumen.setText(
            f"Coste g(n): {coste_g:.1f} min | Paradas: {len(ruta)} | Transbordos: {num_transbordos}"
        )

        for i, est in enumerate(ruta):
            linea = ESTACIONES_METRORREY.get(est, (0, 0, "?"))[2]
            prefijo = "🟢 INICIO:" if i == 0 else ("🏁 DESTINO:" if i == len(ruta) - 1 else f"{i}.")
            texto = f"{prefijo} {est} (Línea {linea})"
            self.lista_pasos.addItem(texto)

        if transbordos:
            self.lista_pasos.addItem("──────────────────────────")
            for t in transbordos:
                self.lista_pasos.addItem(f"🔄 Transbordo en: {t}")