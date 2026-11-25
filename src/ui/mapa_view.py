import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.ui.estilos import (
    COLOR_FONDO_APP,
    COLOR_FONDO_PANEL,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_RUTA_BRILLO,
    COLOR_TRANSBORDO,
    COLOR_LINEA_1,
    COLOR_LINEA_2,
    COLOR_LINEA_3,
)

# Datos provisionales de las 3 líneas (misma estructura que definirá Adrián)
LINEAS_METRORREY = {
    "L1": {
        "numero": "1",
        "color": COLOR_LINEA_1,
        "estaciones": [
            "Talleres", "San Bernabé", "Unidad Modelo", "Aztlán",
            "Penitenciaría", "Alfonso Reyes", "Mitras", "Simón Bolívar",
            "Hospital", "Edison", "Central", "Cuauhtémoc", "Del Golfo",
            "Félix U. Gómez", "Parque Fundidora", "Y Griega",
            "Eloy Cavazos", "Lerdo de Tejada", "Exposición"
        ],
    },
    "L2": {
        "numero": "2",
        "color": COLOR_LINEA_2,
        "estaciones": [
            "Sendero", "Santiago Tapia", "San Nicolás", "Anáhuac",
            "Universidad", "Niños Héroes", "Regina", "Gral. Anaya",
            "Cuauhtémoc", "Alameda", "Fundadores", "Padre Mier",
            "Gral. I. Zaragoza"
        ],
    },
    "L3": {
        "numero": "3",
        "color": COLOR_LINEA_3,
        "estaciones": [
            "Gral. I. Zaragoza", "Santa Lucía", "Col. Obrera",
            "Félix U. Gómez", "Metalúrgicos", "Col. Moderna",
            "Ruiz Cortines", "Los Ángeles", "Hospital Metropolitano"
        ],
    },
}

# Estaciones subterráneas según la simbología del plano oficial
ESTACIONES_SUBTERRANEAS = {
    "Regina", "Gral. Anaya", "Cuauhtémoc", "Alameda",
    "Fundadores", "Padre Mier", "Gral. I. Zaragoza"
}

# Los 3 transbordos oficiales del enunciado
ESTACIONES_TRANSBORDO = {
    "Cuauhtémoc", "Gral. I. Zaragoza", "Félix U. Gómez"
}

# Coordenadas esquemáticas fieles al plano oficial de Metrorrey
POSICIONES_ESQUEMATICAS = {
    # Línea 1 (Amarilla)
    "Talleres": (0.0, 14.0),
    "San Bernabé": (1.0, 13.0),
    "Unidad Modelo": (2.0, 12.0),
    "Aztlán": (3.0, 11.0),
    "Penitenciaría": (4.0, 10.0),
    "Alfonso Reyes": (4.0, 8.8),
    "Mitras": (4.0, 7.6),
    "Simón Bolívar": (4.0, 6.4),
    "Hospital": (4.0, 5.0),
    "Edison": (5.5, 5.0),
    "Central": (7.0, 5.0),
    "Cuauhtémoc": (8.5, 5.0),
    "Del Golfo": (10.2, 5.0),
    "Félix U. Gómez": (12.0, 5.0),
    "Parque Fundidora": (13.5, 4.0),
    "Y Griega": (15.0, 3.5),
    "Eloy Cavazos": (16.8, 3.5),
    "Lerdo de Tejada": (18.6, 3.5),
    "Exposición": (20.4, 3.5),
    # Línea 2 (Verde)
    "Sendero": (11.0, 14.5),
    "Santiago Tapia": (10.6, 13.3),
    "San Nicolás": (10.2, 12.1),
    "Anáhuac": (9.8, 10.9),
    "Universidad": (9.4, 9.7),
    "Niños Héroes": (9.0, 8.5),
    "Regina": (8.7, 7.3),
    "Gral. Anaya": (8.5, 6.1),
    "Alameda": (8.5, 3.8),
    "Fundadores": (8.5, 2.6),
    "Padre Mier": (8.5, 1.4),
    "Gral. I. Zaragoza": (10.0, 1.4),
    # Línea 3 (Roja)
    "Santa Lucía": (10.8, 2.6),
    "Col. Obrera": (11.4, 3.8),
    "Metalúrgicos": (12.6, 6.2),
    "Col. Moderna": (13.2, 7.4),
    "Ruiz Cortines": (14.2, 8.5),
    "Los Ángeles": (15.4, 9.5),
    "Hospital Metropolitano": (16.6, 10.5),
}


class MapaMetrorreyView:
    def __init__(self, parent, lineas_data=None, posiciones=None):
        self.lineas = lineas_data or LINEAS_METRORREY
        self.posiciones = posiciones or POSICIONES_ESQUEMATICAS
        self.ruta_actual = []
        self.transbordos_activos = set()

        self.fig, self.ax = plt.subplots(figsize=(9, 7), dpi=100)
        self.fig.patch.set_facecolor(COLOR_FONDO_APP)
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.03)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.dibujar()

    @staticmethod
    def _normalizar_nombre(estacion):
        """Limpia sufijos tipo '_L1' o ' (L1)' si el grafo desdobla nodos de transbordo."""
        nombre = str(estacion).strip()
        for sep in ("_L", " (L"):
            if sep in nombre:
                nombre = nombre.split(sep)[0].strip()
        return nombre

    def actualizar_ruta(self, ruta, transbordos=None):
        """Método público para resaltar una ruta calculada por A*."""
        ruta_limpia = []
        for est in (ruta or []):
            nombre = self._normalizar_nombre(est)
            # Evitar duplicados consecutivos si hay nodo desdoblado de transbordo
            if not ruta_limpia or ruta_limpia[-1] != nombre:
                ruta_limpia.append(nombre)

        self.ruta_actual = ruta_limpia
        self.transbordos_activos = {
            self._normalizar_nombre(t) for t in (transbordos or [])
        }
        self.dibujar()

    def limpiar_ruta(self):
        """Restaura el mapa al estado inicial sin ruta seleccionada."""
        self.ruta_actual = []
        self.transbordos_activos = set()
        self.dibujar()

    def _color_segmento(self, u, v):
        for info in self.lineas.values():
            est = info["estaciones"]
            for i in range(len(est) - 1):
                if {est[i], est[i + 1]} == {u, v}:
                    return info["color"]
        return "#FFFFFF"

    def _offset_etiqueta(self, estacion):
        # Central abajo sin rotación para no chocar con Cuauhtémoc ni Alameda
        if estacion == "Central":
            return (0.0, -0.42), "center", "top", 0

        # Tramo horizontal L1 + ramal este
        if estacion in {
            "Edison", "Del Golfo", "Parque Fundidora",
            "Y Griega", "Eloy Cavazos", "Lerdo de Tejada", "Exposición"
        }:
            return (0.0, -0.45), "center", "top", -35

        # Tramo noroeste/vertical L1
        if estacion in {
            "Talleres", "San Bernabé", "Unidad Modelo", "Aztlán",
            "Penitenciaría", "Alfonso Reyes", "Mitras",
            "Simón Bolívar", "Hospital"
        }:
            return (-0.35, 0.0), "right", "center", 0

        # Tramo vertical L2
        if estacion in {
            "Sendero", "Santiago Tapia", "San Nicolás", "Anáhuac",
            "Universidad", "Niños Héroes", "Regina", "Gral. Anaya",
            "Alameda", "Fundadores", "Padre Mier"
        }:
            return (-0.35, 0.0), "right", "center", 0

        # Los 3 transbordos en huecos limpios
        if estacion == "Cuauhtémoc":
            return (-0.30, 0.35), "right", "bottom", 0
        if estacion == "Félix U. Gómez":
            return (-0.35, 0.35), "right", "bottom", 0
        if estacion == "Gral. I. Zaragoza":
            return (0.0, -0.45), "center", "top", 0

        # Línea 3 hacia el noreste
        return (0.35, 0.0), "left", "center", 0

    def _dibujar_leyenda_y_badges(self):
        badges = [
            ("L1", COLOR_LINEA_1, (0.0, 14.9)),
            ("L2", COLOR_LINEA_2, (11.0, 15.4)),
            ("L3", COLOR_LINEA_3, (16.6, 11.4)),
        ]
        for texto, color, (bx, by) in badges:
            self.ax.text(
                bx, by, texto, color="white", fontweight="bold", fontsize=9,
                ha="center", va="center", zorder=18,
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor=color,
                    edgecolor="white",
                    linewidth=1.5,
                ),
            )

        elementos_leyenda = [
            Line2D([0], [0], color=COLOR_LINEA_1, lw=3.5, label="Línea 1"),
            Line2D([0], [0], color=COLOR_LINEA_2, lw=3.5, label="Línea 2"),
            Line2D([0], [0], color=COLOR_LINEA_3, lw=3.5, label="Línea 3"),
            Line2D([0], [0], color=COLOR_RUTA_BRILLO, lw=4.5, label="Ruta óptima"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#FFFFFF",
                   markeredgecolor=COLOR_FONDO_APP, markersize=7, label="Estación elevada"),
            Line2D([0], [0], marker="s", color="none", markerfacecolor="#FFFFFF",
                   markeredgecolor=COLOR_FONDO_APP, markersize=7, label="Estación subterránea"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#FFFFFF",
                   markeredgecolor=COLOR_TRANSBORDO, markeredgewidth=2, markersize=8,
                   label="Correspondencia"),
        ]
        leyenda = self.ax.legend(
            handles=elementos_leyenda,
            loc="upper right",
            frameon=True,
            facecolor=COLOR_FONDO_APP,
            edgecolor="#44475A",
            fontsize=8,
            labelcolor=COLOR_TEXTO_PRINCIPAL,
        )
        leyenda.set_zorder(20)

    def dibujar(self):
        self.ax.clear()
        self.ax.set_facecolor(COLOR_FONDO_PANEL)

        # 1. Dibujar las 3 líneas base
        for info in self.lineas.values():
            estaciones = info["estaciones"]
            for i in range(len(estaciones) - 1):
                x0, y0 = self.posiciones[estaciones[i]]
                x1, y1 = self.posiciones[estaciones[i + 1]]
                self.ax.plot(
                    [x0, x1], [y0, y1],
                    color=info["color"], linewidth=4.5,
                    zorder=2, solid_capstyle="round"
                )

        # 2. Resaltar la ruta calculada (si existe)
        if len(self.ruta_actual) > 1:
            for i in range(len(self.ruta_actual) - 1):
                u, v = self.ruta_actual[i], self.ruta_actual[i + 1]
                if u in self.posiciones and v in self.posiciones:
                    x0, y0 = self.posiciones[u]
                    x1, y1 = self.posiciones[v]
                    # Halo exterior cian brillante
                    self.ax.plot(
                        [x0, x1], [y0, y1],
                        color=COLOR_RUTA_BRILLO, linewidth=10.5,
                        zorder=6, solid_capstyle="round"
                    )
                    # Interior con el color original de la línea
                    self.ax.plot(
                        [x0, x1], [y0, y1],
                        color=self._color_segmento(u, v), linewidth=4.5,
                        zorder=7, solid_capstyle="round"
                    )

        # 3. Dibujar estaciones y etiquetas
        ruta_set = set(self.ruta_actual)
        for estacion, (x, y) in self.posiciones.items():
            es_sub = estacion in ESTACIONES_SUBTERRANEAS
            es_transbordo = estacion in ESTACIONES_TRANSBORDO
            en_ruta = estacion in ruta_set
            marcador = "s" if es_sub else "o"

            self.ax.scatter(
                x, y,
                s=95 if en_ruta else (75 if es_transbordo else 60),
                marker=marcador,
                color=COLOR_RUTA_BRILLO if en_ruta else "#FFFFFF",
                edgecolors=COLOR_TRANSBORDO if es_transbordo else COLOR_FONDO_APP,
                linewidths=2.0 if (es_transbordo or en_ruta) else 1.4,
                zorder=10,
            )

            # Doble anillo destacado si se hace transbordo en esta estación
            if estacion in self.transbordos_activos:
                self.ax.scatter(
                    x, y, s=240, marker=marcador,
                    facecolors="none", edgecolors=COLOR_RUTA_BRILLO,
                    linewidths=2.5, zorder=11,
                )

            (ox, oy), ha, va, rot = self._offset_etiqueta(estacion)
            self.ax.text(
                x + ox, y + oy, estacion,
                color=COLOR_RUTA_BRILLO if en_ruta else COLOR_TEXTO_PRINCIPAL,
                fontsize=8.0 if en_ruta else 7.5,
                fontweight="bold" if (en_ruta or es_transbordo) else "normal",
                ha=ha, va=va, rotation=rot, zorder=12,
            )

        self._dibujar_leyenda_y_badges()

        self.ax.set_xlim(-2.5, 22.2)
        self.ax.set_ylim(-0.5, 16.3)
        self.ax.axis("off")
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba Mapa Metrorrey - Paso 4 (Ruta Simulada)")
    root.geometry("1000x750")
    root.configure(bg=COLOR_FONDO_APP)

    vista = MapaMetrorreyView(root)
    # Simulamos una ruta con 2 transbordos (Universidad -> Hospital Metropolitano)
    vista.actualizar_ruta(
        [
            "Universidad", "Niños Héroes", "Regina", "Gral. Anaya",
            "Cuauhtémoc", "Del Golfo", "Félix U. Gómez",
            "Metalúrgicos", "Col. Moderna", "Ruiz Cortines",
            "Los Ángeles", "Hospital Metropolitano"
        ],
        transbordos=["Cuauhtémoc", "Félix U. Gómez"],
    )

    root.protocol("WM_DELETE_WINDOW", lambda: (plt.close("all"), root.destroy()))
    root.mainloop()