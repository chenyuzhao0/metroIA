"""Punto de entrada principal de la aplicación Metrorrey (A*)."""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.algorithm.astar import calcular_ruta_astar


def main() -> None:
    app = QApplication(sys.argv)
    ventana = MainWindow(callback_calcular_ruta=calcular_ruta_astar)
    ventana.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
