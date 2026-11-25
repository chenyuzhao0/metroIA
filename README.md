# Metro de Monterrey (Metrorrey) — Búsqueda A*

Práctica de Inteligencia Artificial (curso 2026-27): aplicación con interfaz gráfica para calcular el trayecto óptimo entre dos estaciones de las líneas 1, 2 y 3 de Metrorrey mediante el algoritmo A*.

## Estructura del proyecto

- `data/`: ficheros de datos (estaciones, conexiones, coordenadas, transbordos y metadatos).
- `assets/`: recursos gráficos (p. ej., plano del metro).
- `src/model/`: carga de datos, representación del grafo y funciones `g(n)` y `h(n)`.
- `src/algorithm/`: implementación del algoritmo A*.
- `src/ui/`: interfaz gráfica de usuario.
- `tests/`: pruebas unitarias y de verificación de rutas.
- `docs/`: borradores, notas y capturas para la memoria.
- `main.py`: punto de entrada principal de la aplicación.

## Instalación y ejecución

1. Clonar el repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd metrorrey
   ```

2. Crear y activar el entorno virtual:
   ```bash
   python3 -m venv .venv
   # En Linux / macOS:
   source .venv/bin/activate
   # En Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Flujo de trabajo en equipo (Git)

- No trabajar directamente sobre `main`.
- Crear una rama por módulo o tarea (`git checkout -b feature/datos`, `feature/algoritmo`, `feature/interfaz`, etc.).
- Integrar cambios mediante Pull Requests revisadas por otro compañero.
