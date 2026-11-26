// Plantilla base de Memoria — Práctica Inteligencia Artificial (Metrorrey A*)
// Compilar a PDF: typst compile memoria.typ memoria.pdf
// Límite de subida en Moodle: < 20 MB (entrega: 2 de diciembre de 2026 antes de las 24:00)

#set document(
  title: "Práctica de Inteligencia Artificial: Metro de Monterrey (Metrorrey)",
  author: "Grupo X — Inteligencia Artificial (UPM)",
)

#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2.5cm),
  numbering: "1",
  number-align: right,
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8.5pt, fill: luma(110))
      Inteligencia Artificial GII (+ ADE) — Práctica Metrorrey (A\*)
      #h(1fr)
      Curso 2026-27
      #line(length: 100%, stroke: 0.4pt + luma(180))
    ]
  },
)

#set text(
  lang: "es",
  size: 11pt,
)

#set par(
  justify: true,
  leading: 0.65em,
)

#set heading(numbering: "1.1.")

#show heading.where(level: 1): it => {
  v(0.8em)
  text(size: 14pt, weight: "bold", it)
  v(0.3em)
}

#let todo(texto) = block(
  fill: rgb("#FEF3C7"),
  stroke: 0.8pt + rgb("#F59E0B"),
  radius: 4pt,
  inset: 8pt,
  width: 100%,
)[
  #set text(size: 9.5pt, fill: rgb("#92400E"))
  *Por completar:* #texto
]

// ============================================================================
// 1. PORTADA (Apartado 1 obligatorio)
// ============================================================================
#page(numbering: none, header: none)[
  #align(center)[
    #v(1.5cm)
    #text(size: 13pt, weight: "semibold")[Universidad Politécnica de Madrid] \
    #text(size: 11pt, fill: luma(80))[Escuela Técnica Superior de Ingenieros Informáticos]

    #v(2.5cm)
    #line(length: 85%, stroke: 1.5pt + rgb("#1E3A8A"))
    #v(0.8cm)
    #text(size: 22pt, weight: "bold")[Inteligencia Artificial] \
    #v(0.3cm)
    #text(size: 16pt, weight: "medium")[Práctica: Cálculo de trayectos óptimos en el Metro de Monterrey (Metrorrey) mediante A\*]
    #v(0.8cm)
    #line(length: 85%, stroke: 1.5pt + rgb("#1E3A8A"))

    #v(2.5cm)
    #align(left)[
      #pad(left: 1.5cm, right: 1.5cm)[
        #table(
          columns: (auto, 1fr),
          stroke: none,
          row-gutter: 8pt,
          [*Curso académico:*], [2026-27],
          [*Titulación:*], [[Completar: Ingeniería Informática / Ingeniería Informática + ADE]],
          [*Número de grupo:*], [[Completar: Grupo Nº ...]],
          [*Grupo de clase (del coordinador):*], [[Completar: 1M / 1MB / 2M / 2MB]],
          [*Coordinador del grupo:*], [[Completar: Nombre y Apellidos]],
          [*Miembros del grupo:*], [
            - [Nombre y Apellidos 1] _(Coordinador)_
            - [Nombre y Apellidos 2]
            - [Nombre y Apellidos 3]
            - [Nombre y Apellidos 4]
            - [Nombre y Apellidos 5]
            - [Nombre y Apellidos 6]
          ],
          [*Fecha de entrega:*], [2 de diciembre de 2026],
        )
      ]
    ]
  ]
]

// Índice automático
#outline(title: "Índice", indent: auto)
#pagebreak()

// ============================================================================
// 2. INTRODUCCIÓN (Apartado 2 obligatorio)
// ============================================================================
= Introducción

#todo[Describir el problema a resolver (cálculo del trayecto óptimo en las líneas 1, 2 y 3 de Metrorrey y los 3 transbordos permitidos: Cuauhtémoc, General Ignacio Zaragoza y Félix U. Gómez) y los objetivos técnicos y funcionales a alcanzar con la aplicación.]

== Descripción del problema

== Objetivos

// ============================================================================
// 3. DESARROLLO DE LA PRÁCTICA: MODELADO Y ALGORITMO A* (Apartado 3 obligatorio)
// ============================================================================
= Descripción del desarrollo de la práctica

#todo[Explicar con detalle el modelado del grafo (nodos estación-línea, aristas de tramo y transbordo), los datos tenidos en cuenta y las fórmulas exactas de $g(n)$ y $h(n)$, incluyendo la justificación de consistencia/admisibilidad.]

== Modelado de la red de Metrorrey y datos considerados
#todo[Indicar líneas contempladas (L1 Talleres–Exposición, L2 Sendero–Gral. I. Zaragoza, L3 Gral. I. Zaragoza–Hospital Metropolitano), transbordos, atributos usados (coordenadas GPS, subterráneas/elevadas, ascensores, escaleras, aforo, cortes de servicio, franjas horarias/afluencia).]

== Función de coste real $g(n)$
#todo[Escribir la expresión matemática exacta de $g(n)$ en minutos para tramos normales y para transbordos, especificando constantes (velocidad comercial, tiempo de parada, penalizaciones por afluencia, movilidad reducida y longitud de transbordo) y cómo se tratan las incidencias/cortes.]

// Ejemplo de bloque matemático en Typst (sustituir por vuestra fórmula exacta):
$ g(n) = g("padre"(n)) + c("padre"(n), n) $

== Función heurística $h(n)$ y análisis de admisibilidad
#todo[Detallar el cálculo de la distancia geodésica mediante la fórmula de Haversine, la conversión a minutos usando la velocidad máxima $v_max$, y demostrar por qué $h(n)$ es consistente ($h(n) <= c(n, m) + h(m)$) y minorante/admisible ($h(n) <= h^*(n)$) en todos los modos de la aplicación.]

$ f(n) = g(n) + h(n) $

== Algoritmo de búsqueda A\*
#todo[Describir el funcionamiento implementado (lista abierta con cola de prioridad `heapq`, lista cerrada, actualización de $g(n)$, reconstrucción del camino, detección de transbordos y validación experimental frente a Dijkstra con $h(n) = 0$).]

// ============================================================================
// 4. DISEÑO E IMPLEMENTACIÓN DE LA APLICACIÓN (Apartado 4 obligatorio)
// ============================================================================
= Diseño e implementación de la aplicación

#todo[Incluir arquitectura de módulos (`data/`, `src/model/`, `src/algorithm/`, `src/ui/`, `main.py`, `tests/`), capturas de pantalla comentadas del código relevante, capturas comentadas de la interfaz gráfica y ejemplos de ejecución variados (misma línea, con transbordos, movilidad reducida, hora punta, estación cortada).]

== Arquitectura y estructura del proyecto

== Implementación del código (capturas comentadas)

// Ejemplo para insertar capturas:
// #figure(
//   image("capturas/codigo_astar.png", width: 90%),
//   caption: [Implementación del bucle principal de A\*.],
// )

== Interfaz de usuario (capturas comentadas)

== Ejemplos de ejecución

// ============================================================================
// 5. CÓDIGO FUENTE E INSTRUCCIONES DE EJECUCIÓN (Apartado 5 obligatorio)
// ============================================================================
= Código fuente

#todo[Incluir el enlace descargable/público al repositorio de GitHub y las instrucciones paso a paso verificadas en un equipo limpio para instalar dependencias y ejecutar la aplicación.]

== Enlace al repositorio
- *Repositorio GitHub:* `[Completar con URL pública, p. ej. https://github.com/chenyuzhao0/metroIA]`

== Requisitos e instrucciones de ejecución
```bash
git clone <URL_DEL_REPOSITORIO>
cd metrorrey
python3 -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

// ============================================================================
// 6. CONCLUSIONES TÉCNICAS Y DE GESTIÓN DEL GRUPO (Apartado 6 obligatorio)
// ============================================================================
= Conclusiones técnicas y de gestión del grupo

#todo[Cubrir todos los puntos pedidos en el enunciado: dificultades encontradas, aspectos positivos, lecciones aprendidas, qué se ha hecho bien como grupo, qué se debería mejorar en la próxima ocasión, y habilidades interpersonales (sensaciones del grupo, ambiente, comunicación, acuerdos, reparto de tareas, gestión de conflictos y aspectos humanos).]

== Conclusiones técnicas

== Gestión del grupo y habilidades interpersonales

// ============================================================================
// 7. REFERENCIAS (Apartado 7 obligatorio)
// ============================================================================
= Referencias

#todo[Enumerar todas las librerías empleadas indicando su propósito, y listar todas las fuentes consultadas para estaciones, coordenadas GPS, características de líneas/transbordos, velocidades y horarios de Metrorrey.]

== Librerías y herramientas empleadas
#table(
  columns: (auto, 1fr),
  [*Librería / Herramienta*], [*Objeto de utilización*],
  [`PySide6`], [[Completar descripción]],
  [`heapq` (biblioteca estándar)], [[Completar descripción]],
  [`math` (biblioteca estándar)], [[Completar descripción]],
  [`json` (biblioteca estándar)], [[Completar descripción]],
)

== Fuentes de datos y bibliografía
- [Fuente 1: Metrorrey / OpenStreetMap / transparencias de la asignatura, etc.]

// ============================================================================
// 8. UTILIZACIÓN DE HERRAMIENTAS DE INTELIGENCIA ARTIFICIAL (Apartado 8 obligatorio)
// ============================================================================
= Utilización de herramientas de inteligencia artificial

#todo[Apartado obligatorio y crítico: si se han utilizado herramientas de IA como apoyo didáctico (ideas, resolución de dudas, revisión de errores, diseño de estructura), detallar cada tarea concreta, herramienta/modelo empleado, motivo de uso, transcripción de los prompts, salidas obtenidas, justificación de qué se aceptó y qué se descartó, y cómo se revisaron y validaron los resultados. Recordar que cualquier uso no declarado conlleva la anulación de la práctica (0 puntos).]

#table(
  columns: (auto, auto, 1fr, 1fr),
  [*Tarea*], [*Herramienta / Modelo*], [*Prompt y motivo de uso*], [*Qué se aceptó/descartó y validación*],
  [[Ej. Planificación y revisión técnica]], [[Completar]], [[Completar]], [[Completar]],
)
