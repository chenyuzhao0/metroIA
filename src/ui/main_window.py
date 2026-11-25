import json
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QListWidget, QFrame, QSlider, QTimeEdit,
    QGridLayout, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QTime
from src.ui.mapa_widget import MapaMetrorreyView

HORA_APERTURA_MIN = 5 * 60            # 05:00
HORA_CIERRE_MADRUGADA = 1 * 60 + 30   # 01:30
TIEMPO_MEDIO_TRAMO_MIN = 3.0          # 3 min por tramo
TIEMPO_PARADA_MIN = 0.5               # 30 s en cada estación


def cargar_json_red():
    raiz_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    carpeta_data = os.path.join(raiz_proyecto, "data")
    if os.path.exists(carpeta_data):
        for archivo in os.listdir(carpeta_data):
            if archivo.endswith(".json"):
                with open(os.path.join(carpeta_data, archivo), "r", encoding="utf-8") as f:
                    return json.load(f)
    raise FileNotFoundError(f"No se encontró ningún archivo .json en '{carpeta_data}'")


class MainWindow(QMainWindow):
    def __init__(self, callback_calcular_ruta=None):
        super().__init__()
        self.callback_calcular_ruta = callback_calcular_ruta
        self.datos_red = cargar_json_red()
        self.estaciones = self.datos_red["estaciones"]
        self.turno_clic_origen = True
        self.nivel_afluencia_actual = "media"
        self.metro_abierto = True

        self.setWindowTitle("Metrorrey A* — Planificador de Trayecto Óptimo (Líneas 1, 2 y 3)")
        self.resize(1460, 880)
        self._aplicar_estilos()
        self._construir_interfaz()

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #EEF2F6; }
            QFrame#HeaderCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F2C59, stop:1 #1D4ED8);
                border-radius: 12px;
            }
            QLabel#TituloApp { font-size: 19px; font-weight: 800; color: #FFFFFF; }
            QLabel#SubtituloApp { font-size: 12px; color: #DBEAFE; }
            QFrame.Tarjeta {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
            QLabel.SeccionTitulo { font-size: 13px; font-weight: 700; color: #0F2C59; }
            QLabel.CampoLabel { font-size: 12px; font-weight: 600; color: #475569; }
            QComboBox, QTimeEdit {
                padding: 7px 10px;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                background-color: #F8FAFC;
                font-size: 13px;
                color: #0F172A;
                font-weight: 600;
            }
            QComboBox:hover, QTimeEdit:hover { border-color: #3B82F6; background-color: #FFFFFF; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                selection-background-color: #DBEAFE;
                selection-color: #0F2C59;
                border: 1.5px solid #94A3B8;
                outline: 0px;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 26px;
                padding: 4px 8px;
                color: #0F172A;
            }
            QPushButton#BtnMini {
                background-color: #F1F5F9;
                color: #0F2C59;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#BtnMini:hover { background-color: #E2E8F0; }
            QPushButton.ToggleOpcion {
                background-color: #F8FAFC;
                color: #334155;
                border: 1.5px solid #CBD5E1;
                border-radius: 9px;
                padding: 9px 12px;
                text-align: left;
                font-size: 12.5px;
                font-weight: 600;
            }
            QPushButton.ToggleOpcion:hover { border-color: #60A5FA; background-color: #EFF6FF; }
            QPushButton.ToggleOpcion:checked {
                background-color: #DBEAFE;
                color: #0F2C59;
                border: 1.5px solid #2563EB;
                font-weight: 700;
            }
            QSlider::groove:horizontal { height: 6px; background: #E2E8F0; border-radius: 3px; }
            QSlider::handle:horizontal {
                background: #0F2C59; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px;
            }
            QSlider::sub-page:horizontal { background: #3B82F6; border-radius: 3px; }
            QPushButton#BtnCalcular {
                background-color: #E11D48; color: #FFFFFF; font-weight: 700;
                font-size: 14px; padding: 11px; border-radius: 9px;
            }
            QPushButton#BtnCalcular:hover { background-color: #BE123C; }
            QPushButton#BtnCalcular:disabled { background-color: #94A3B8; color: #E2E8F0; }
            QPushButton#BtnLimpiar {
                background-color: #E2E8F0; color: #334155; font-weight: 700;
                font-size: 13px; padding: 11px; border-radius: 9px;
            }
            QPushButton#BtnLimpiar:hover { background-color: #CBD5E1; }
            QListWidget {
                border: 1px solid #E2E8F0; border-radius: 8px;
                background-color: #F8FAFC; color: #0F172A; font-size: 12.5px; padding: 4px;
            }
            QListWidget::item { padding: 5px 6px; border-bottom: 1px solid #F1F5F9; color: #0F172A; }
        """)

    def _crear_tarjeta(self):
        tarjeta = QFrame()
        tarjeta.setProperty("class", "Tarjeta")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(14)
        sombra.setOffset(0, 3)
        sombra.setColor(QColor(15, 44, 89, 18))
        tarjeta.setGraphicsEffect(sombra)
        return tarjeta

    def _construir_interfaz(self):
        contenedor = QWidget()
        layout_principal = QHBoxLayout(contenedor)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        layout_principal.setSpacing(16)

        # --- PANEL IZQUIERDO ---
        panel_control = QWidget()
        panel_control.setFixedWidth(435)
        layout_izq = QVBoxLayout(panel_control)
        layout_izq.setContentsMargins(0, 0, 0, 0)
        layout_izq.setSpacing(11)

        # 0. Cabecera
        header = QFrame()
        header.setObjectName("HeaderCard")
        layout_header = QVBoxLayout(header)
        layout_header.setContentsMargins(16, 12, 16, 12)
        lbl_titulo = QLabel("🚇 METRORREY · Ruta Óptima A*")
        lbl_titulo.setObjectName("TituloApp")
        lbl_subtitulo = QLabel("Servicio: 05:00–01:30 h · 3 min/tramo · 30 s/parada")
        lbl_subtitulo.setObjectName("SubtituloApp")
        layout_header.addWidget(lbl_titulo)
        layout_header.addWidget(lbl_subtitulo)
        layout_izq.addWidget(header)

        # 1. Tarjeta: Origen y Destino
        card_trayecto = self._crear_tarjeta()
        layout_trayecto = QVBoxLayout(card_trayecto)
        layout_trayecto.setContentsMargins(14, 12, 14, 12)
        layout_trayecto.setSpacing(8)

        lbl_sec1 = QLabel("📍 ORIGEN Y DESTINO")
        lbl_sec1.setProperty("class", "SeccionTitulo")
        layout_trayecto.addWidget(lbl_sec1)

        grid_est = QGridLayout()
        grid_est.setSpacing(6)

        lbl_orig = QLabel("Origen:")
        lbl_orig.setProperty("class", "CampoLabel")
        self.combo_origen = QComboBox()

        lbl_dest = QLabel("Destino:")
        lbl_dest.setProperty("class", "CampoLabel")
        self.combo_destino = QComboBox()

        items_ordenados = sorted(
            self.estaciones.items(),
            key=lambda kv: (kv[1]["nombre"], kv[1]["linea"])
        )
        for est_id, info in items_ordenados:
            icono_asc = " ♿" if info.get("ascensor", False) else ""
            etiqueta = f"{info['nombre']} (L{info['linea']}){icono_asc}"
            self.combo_origen.addItem(etiqueta, est_id)
            self.combo_destino.addItem(etiqueta, est_id)

        self._seleccionar_id_en_combo(self.combo_origen, "Talleres_L1")
        self._seleccionar_id_en_combo(self.combo_destino, "Hospital_Metropolitano_L3")

        btn_invertir = QPushButton("⇅")
        btn_invertir.setObjectName("BtnMini")
        btn_invertir.setToolTip("Invertir origen y destino")
        btn_invertir.setFixedWidth(36)
        btn_invertir.clicked.connect(self._invertir_estaciones)

        grid_est.addWidget(lbl_orig, 0, 0)
        grid_est.addWidget(self.combo_origen, 0, 1)
        grid_est.addWidget(lbl_dest, 1, 0)
        grid_est.addWidget(self.combo_destino, 1, 1)
        grid_est.addWidget(btn_invertir, 0, 2, 2, 1)

        layout_trayecto.addLayout(grid_est)
        layout_izq.addWidget(card_trayecto)

        # 2. Tarjeta: Condiciones del Viaje e Incidencias
        card_factores = self._crear_tarjeta()
        layout_factores = QVBoxLayout(card_factores)
        layout_factores.setContentsMargins(14, 12, 14, 12)
        layout_factores.setSpacing(9)

        lbl_sec2 = QLabel("⚙️ CONDICIONES DEL VIAJE (Coste g(n))")
        lbl_sec2.setProperty("class", "SeccionTitulo")
        layout_factores.addWidget(lbl_sec2)

        fila_hora = QHBoxLayout()
        lbl_hora = QLabel("🕒 Hora de salida:")
        lbl_hora.setProperty("class", "CampoLabel")

        self.time_salida = QTimeEdit()
        self.time_salida.setDisplayFormat("HH:mm")
        self.time_salida.setTime(QTime.currentTime())
        self.time_salida.timeChanged.connect(self._evaluar_estado_y_afluencia)

        btn_ahora = QPushButton("Ahora")
        btn_ahora.setObjectName("BtnMini")
        btn_ahora.clicked.connect(lambda: self.time_salida.setTime(QTime.currentTime()))

        fila_hora.addWidget(lbl_hora)
        fila_hora.addWidget(self.time_salida, 1)
        fila_hora.addWidget(btn_ahora)
        layout_factores.addLayout(fila_hora)

        self.lbl_estado_afluencia = QLabel()
        self.lbl_estado_afluencia.setWordWrap(True)
        self.lbl_estado_afluencia.setAlignment(Qt.AlignCenter)
        layout_factores.addWidget(self.lbl_estado_afluencia)

        self.lbl_incidencias = QLabel()
        self.lbl_incidencias.setWordWrap(True)
        self.lbl_incidencias.setStyleSheet("""
            background-color: #FFF1F2; color: #9F1239; border: 1px solid #FDA4AF;
            border-radius: 7px; padding: 6px 8px; font-size: 11.5px; font-weight: 600;
        """)
        layout_factores.addWidget(self.lbl_incidencias)

        self.btn_movilidad = QPushButton("♿  Movilidad reducida: DESACTIVADO")
        self.btn_movilidad.setProperty("class", "ToggleOpcion")
        self.btn_movilidad.setCheckable(True)
        self.btn_movilidad.setCursor(Qt.PointingHandCursor)
        self.btn_movilidad.toggled.connect(self._actualizar_texto_movilidad)
        layout_factores.addWidget(self.btn_movilidad)

        self.lbl_penalizacion = QLabel("🔄 Penalización extra por transbordo: 5 min")
        self.lbl_penalizacion.setProperty("class", "CampoLabel")
        self.slider_transbordo = QSlider(Qt.Horizontal)
        self.slider_transbordo.setRange(0, 15)
        self.slider_transbordo.setValue(5)
        self.slider_transbordo.valueChanged.connect(
            lambda v: self.lbl_penalizacion.setText(f"🔄 Penalización extra por transbordo: {v} min")
        )
        layout_factores.addWidget(self.lbl_penalizacion)
        layout_factores.addWidget(self.slider_transbordo)

        layout_izq.addWidget(card_factores)

        # Botones de acción
        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(8)
        self.btn_calcular = QPushButton("Calcular Ruta Óptima (A*)")
        self.btn_calcular.setObjectName("BtnCalcular")
        self.btn_calcular.setCursor(Qt.PointingHandCursor)
        self.btn_calcular.clicked.connect(self._ejecutar_calculo)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("BtnLimpiar")
        self.btn_limpiar.setCursor(Qt.PointingHandCursor)
        self.btn_limpiar.clicked.connect(self._limpiar_todo)

        layout_botones.addWidget(self.btn_calcular, 3)
        layout_botones.addWidget(self.btn_limpiar, 1)
        layout_izq.addLayout(layout_botones)

        # 3. Tarjeta: Resultados
        card_resultados = self._crear_tarjeta()
        layout_res = QVBoxLayout(card_resultados)
        layout_res.setContentsMargins(14, 12, 14, 12)
        layout_res.setSpacing(6)

        lbl_sec3 = QLabel("📊 ITINERARIO ÓPTIMO")
        lbl_sec3.setProperty("class", "SeccionTitulo")
        layout_res.addWidget(lbl_sec3)

        self.lbl_resumen = QLabel("Selecciona origen y destino para calcular")
        self.lbl_resumen.setStyleSheet("font-weight: 700; color: #0F2C59; font-size: 12.5px;")
        layout_res.addWidget(self.lbl_resumen)

        self.lista_pasos = QListWidget()
        layout_res.addWidget(self.lista_pasos)

        layout_izq.addWidget(card_resultados, 1)

        # --- PANEL DERECHO: PLANO INTERACTIVO ---
        self.mapa_view = MapaMetrorreyView(self.datos_red)
        self.mapa_view.estacion_clicada.connect(self._al_clicar_estacion_en_mapa)
        self.mapa_view.estacion_toggle_corte.connect(self._toggle_corte_estacion)

        # Conectar cambio de origen al monigote "Estás aquí"
        self.combo_origen.currentIndexChanged.connect(self._actualizar_monigote_origen)

        layout_principal.addWidget(panel_control)
        layout_principal.addWidget(self.mapa_view, 1)
        self.setCentralWidget(contenedor)

        self._actualizar_monigote_origen()
        self._evaluar_estado_y_afluencia(self.time_salida.time())
        self._actualizar_resumen_incidencias()

    def _actualizar_monigote_origen(self):
        origen_id = self.combo_origen.currentData()
        if origen_id:
            self.mapa_view.marcar_origen_monigote(origen_id)

    def _seleccionar_id_en_combo(self, combo, est_id):
        idx = combo.findData(est_id)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _actualizar_resumen_incidencias(self):
        cortadas = [
            f"{info['nombre']} (L{info['linea']})"
            for info in self.estaciones.values()
            if info.get("cortada", False)
        ]
        if cortadas:
            self.lbl_incidencias.setText(
                f"⚠️ Incidencias activas: {', '.join(cortadas)}\n(Clic derecho en cualquier nodo del mapa para cortar/abrir)"
            )
            self.lbl_incidencias.setVisible(True)
        else:
            self.lbl_incidencias.setText("✅ Todas las estaciones operativas (Clic derecho en mapa para simular corte)")

    def _toggle_corte_estacion(self, est_id):
        if est_id in self.estaciones:
            estado_actual = self.estaciones[est_id].get("cortada", False)
            self.estaciones[est_id]["cortada"] = not estado_actual
            self.mapa_view._dibujar_estado_cortes()
            self._actualizar_resumen_incidencias()

    def _actualizar_texto_movilidad(self, activo):
        if activo:
            self.btn_movilidad.setText("♿  Movilidad reducida: ACTIVADO (requiere ascensor)")
        else:
            self.btn_movilidad.setText("♿  Movilidad reducida: DESACTIVADO")

    def _evaluar_estado_y_afluencia(self, qtime):
        minutos_dia = qtime.hour() * 60 + qtime.minute()
        abierto = (minutos_dia >= HORA_APERTURA_MIN) or (minutos_dia <= HORA_CIERRE_MADRUGADA)
        self.metro_abierto = abierto
        self.mapa_view.set_servicio_activo(abierto)

        if not abierto:
            self.nivel_afluencia_actual = "cerrado"
            self.lbl_estado_afluencia.setText(
                "⛔ SERVICIO CERRADO (01:31 – 04:59 h)\nSin trenes en circulación · Reabre a las 05:00 h"
            )
            self.lbl_estado_afluencia.setStyleSheet("""
                background-color: #FEE2E2; color: #991B1B; border: 1.5px solid #EF4444;
                border-radius: 8px; padding: 8px; font-weight: 700; font-size: 12px;
            """)
            self.btn_calcular.setEnabled(False)
            self.btn_calcular.setText("Servicio Cerrado (05:00 - 01:30)")
            return

        self.btn_calcular.setEnabled(True)
        self.btn_calcular.setText("Calcular Ruta Óptima (A*)")

        hora = qtime.hour()
        if (7 <= hora <= 9) or (17 <= hora <= 20):
            self.nivel_afluencia_actual = "alta"
            self.lbl_estado_afluencia.setText(
                "🔴 AFLUENCIA ALTA · Hora Punta (07:00–09:59 / 17:00–20:59)\nPenalización por saturación de aforo"
            )
            self.lbl_estado_afluencia.setStyleSheet("""
                background-color: #FEF2F2; color: #991B1B; border: 1.5px solid #F87171;
                border-radius: 8px; padding: 8px; font-weight: 600; font-size: 11.5px;
            """)
        elif (10 <= hora <= 16) or (21 <= hora <= 22):
            self.nivel_afluencia_actual = "media"
            self.lbl_estado_afluencia.setText(
                "🟡 AFLUENCIA MEDIA · Horario Regular (10:00–16:59 / 21:00–22:59)\nFrecuencia de paso estándar"
            )
            self.lbl_estado_afluencia.setStyleSheet("""
                background-color: #FFFBEB; color: #92400E; border: 1.5px solid #FBBF24;
                border-radius: 8px; padding: 8px; font-weight: 600; font-size: 11.5px;
            """)
        else:
            self.nivel_afluencia_actual = "baja"
            self.lbl_estado_afluencia.setText(
                "🟢 AFLUENCIA BAJA · Horario Valle / Nocturno (05:00–06:59 / 23:00–01:30)\nTránsito fluido sin aglomeraciones"
            )
            self.lbl_estado_afluencia.setStyleSheet("""
                background-color: #F0FDF4; color: #166534; border: 1.5px solid #4ADE80;
                border-radius: 8px; padding: 8px; font-weight: 600; font-size: 11.5px;
            """)

    def _invertir_estaciones(self):
        idx_o = self.combo_origen.currentIndex()
        idx_d = self.combo_destino.currentIndex()
        self.combo_origen.setCurrentIndex(idx_d)
        self.combo_destino.setCurrentIndex(idx_o)

    def _al_clicar_estacion_en_mapa(self, est_id):
        if self.turno_clic_origen:
            self._seleccionar_id_en_combo(self.combo_origen, est_id)
        else:
            self._seleccionar_id_en_combo(self.combo_destino, est_id)
        self.turno_clic_origen = not self.turno_clic_origen

    def _limpiar_todo(self):
        self.mapa_view.limpiar_ruta()
        self.mapa_view.cerrar_tarjeta_estacion()
        self.lista_pasos.clear()
        self.lbl_resumen.setText("Selecciona origen y destino para calcular")

    def _ejecutar_calculo(self):
        if not self.metro_abierto:
            return

        origen_id = self.combo_origen.currentData()
        destino_id = self.combo_destino.currentData()

        parametros = {
            "origen": origen_id,
            "destino": destino_id,
            "datos_red": self.datos_red,
            "hora_salida": self.time_salida.time().toString("HH:mm"),
            "afluencia": self.nivel_afluencia_actual,
            "movilidad_reducida": self.btn_movilidad.isChecked(),
            "penalizacion_transbordo": self.slider_transbordo.value(),
            "tiempo_medio_tramo_min": TIEMPO_MEDIO_TRAMO_MIN,
            "tiempo_parada_min": TIEMPO_PARADA_MIN,
        }

        if self.callback_calcular_ruta:
            resultado = self.callback_calcular_ruta(parametros)
            if not resultado or not resultado.get("ruta"):
                self.mapa_view.limpiar_ruta()
                self.lista_pasos.clear()
                self.lbl_resumen.setText("⚠️ No existe ruta disponible (estaciones/tramos cortados)")
                return

            self.mostrar_resultado(
                ruta=resultado["ruta"],
                tiempo_total=resultado["tiempo_total"],
                transbordos=resultado["transbordos"],
                coste_g=resultado.get("coste_g", resultado["tiempo_total"])
            )
        else:
            ruta_demo = [
                "Talleres_L1", "San_Bernabe_L1", "Unidad_Modelo_L1", "Aztlan_L1",
                "Penitenciaria_L1", "Alfonso_Reyes_L1", "Mitras_L1", "Simon_Bolivar_L1",
                "Hospital_L1", "Edison_L1", "Central_L1", "Cuauhtemoc_L1",
                "Cuauhtemoc_L2", "Alameda_L2", "Fundadores_L2", "Padre_Mier_L2",
                "Zaragoza_L2", "Zaragoza_L3", "Santa_Lucia_L3", "Col_Obrera_L3",
                "Felix_U_Gomez_L3"
            ]
            tramos = len(ruta_demo) - 1
            paradas_intermedias = max(0, len(ruta_demo) - 2)
            tiempo_calc = (tramos * TIEMPO_MEDIO_TRAMO_MIN) + (paradas_intermedias * TIEMPO_PARADA_MIN) + (2 * self.slider_transbordo.value())
            self.mostrar_resultado(
                ruta_demo,
                tiempo_total=tiempo_calc,
                transbordos=["Cuauhtémoc (L1 → L2)", "General I. Zaragoza (L2 → L3)"],
                coste_g=tiempo_calc
            )

    def mostrar_resultado(self, ruta, tiempo_total, transbordos, coste_g):
        self.mapa_view.dibujar_ruta(ruta)
        self.lista_pasos.clear()

        num_transbordos = len(transbordos)
        self.lbl_resumen.setText(
            f"Coste g(n): {coste_g:.1f} min  ·  Nodos: {len(ruta)}  ·  Transbordos: {num_transbordos}"
        )

        for i, est_id in enumerate(ruta):
            info = self.estaciones.get(est_id, {"nombre": est_id, "linea": "?", "ascensor": False})
            icono_asc = " ♿" if info.get("ascensor", False) else ""
            prefijo = "🟢 INICIO:" if i == 0 else ("🏁 DESTINO:" if i == len(ruta) - 1 else f"{i}.")
            self.lista_pasos.addItem(f"{prefijo} {info['nombre']} (Línea {info['linea']}){icono_asc}")

        if transbordos:
            self.lista_pasos.addItem("──────────────────────────")
            for t in transbordos:
                self.lista_pasos.addItem(f"🔄 Transbordo: {t}")