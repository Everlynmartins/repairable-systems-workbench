Workbench Visual de Sistemas Reparables

Descripción general

Repairable Systems Visual Workbench es una aplicación de escritorio independiente para el análisis exploratorio de confiabilidad de sistemas reparables. Proporciona una interfaz visual para introducir datos de fallas, ajustar un modelo de Proceso de Ley de Potencia, generar gráficos diagnósticos y exportar resultados estadísticos.

Este proyecto es una implementación independiente de software basada en métodos estadísticos públicos para NHPP, modelado mediante Proceso de Ley de Potencia y análisis de crecimiento de confiabilidad. No es una publicación oficial, respaldo, certificación ni herramienta validada por ninguna organización normativa, editorial o institución tercera.

Características principales

1. Entrada visual de datos con tablas estilo hoja de cálculo
2. Soporte para datos de un solo ítem, múltiples ítems con un horizonte común de observación, múltiples ítems con diferentes horizontes de observación y datos agrupados por intervalo
3. Estimación de beta, lambda e intensidad de falla z(t)
4. Gráficos de fallas acumuladas, gráficos log log, gráficos QQ, gráficos TTT y gráficos de intensidad
5. Bandas de confianza basadas en bootstrap para las curvas del modelo cuando están habilitadas
6. Evaluación de bondad de ajuste mediante simulación de Cramer von Mises
7. Exportación de gráficos y resúmenes estadísticos
8. Soporte de interfaz multilingüe

Núcleo matemático

La aplicación implementa la forma del Proceso de Ley de Potencia

Lambda(t) = lambda t^beta

z(t) = lambda beta t^(beta menos 1)

Los valores críticos de Cramer von Mises se calculan mediante simulación Monte Carlo en tiempo de ejecución. El programa no incluye tablas reproducidas de valores críticos. En cada simulación, se generan muestras uniformes ordenadas, se vuelve a estimar el parámetro relativo de forma, se calcula la estadística de Cramer von Mises y el cuantil solicitado se usa como umbral crítico.

Los límites de confianza para z(t) se calculan mediante aproximaciones analíticas y procedimientos de bootstrap, según la opción seleccionada. No se usan tabulaciones embebidas para estos cálculos.

Ejemplos de datos

Los ejemplos embebidos son sintéticos y se generan solo para demostración del software. No se copian de ninguna publicación protegida ni de ninguna fuente de datos propietaria.

Estructura del proyecto

run_workbench.py
    Punto de entrada principal utilizado para iniciar la aplicación.

repairable_workbench/i18n.py
    Texto de la interfaz, traducciones, etiquetas y diccionarios de idioma.

repairable_workbench/math_core.py
    Estimación estadística, ajuste de modelo, cálculos de bondad de ajuste, intervalos de confianza, rutinas de bootstrap y generación de valores críticos mediante Monte Carlo.

repairable_workbench/results.py
    Contenedores de resultados y resúmenes estadísticos formateados.

repairable_workbench/plotting.py
    Utilidades de preparación de gráficos y soporte para curvas del modelo.

repairable_workbench/resources.py
    Importación, exportación, guardado, ejemplos sintéticos y recursos auxiliares.

repairable_workbench/ui_components.py
    Componentes visuales reutilizables, incluidas tablas de datos estilo hoja de cálculo.

repairable_workbench/visual.py
    Interfaz gráfica principal y diseño de la aplicación.

Instalación

Se recomienda Python 3.10 o una versión más reciente.

Instale los paquetes requeridos con

pip install numpy scipy matplotlib

Ejecución de la aplicación

Desde la carpeta del proyecto, ejecute

python run_workbench.py

Ejemplo en Windows

cd "C:\Users\Windows\Documents\Projects\modular_workbench_v3"
C:\Users\Windows\AppData\Local\Programs\Python\Python313\python.exe .\run_workbench.py

Si el archivo ZIP crea una carpeta anidada, entre en la carpeta interna que contiene run_workbench.py y el directorio repairable_workbench antes de ejecutar el comando.

Cambio principal reciente

El archivo principal modificado en esta versión es

repairable_workbench/math_core.py

La lógica anterior basada en una tabla fija para el umbral de Cramer von Mises fue reemplazada por la generación de valores críticos mediante Monte Carlo.

Notas de publicación

Este repositorio está destinado a software educativo y de ingeniería independiente. Antes de la publicación pública, evite agregar texto protegido, tablas reproducidas, capturas de pantalla, figuras, logotipos o ejemplos copiados de normas comerciales, libros, manuales o informes internos propietarios.

Nombres recomendados para el repositorio

repairable_systems_workbench
nhpp_reliability_workbench
power_law_process_workbench

Descripción corta sugerida para el repositorio

Workbench visual independiente para análisis de confiabilidad de sistemas reparables usando métodos NHPP y Proceso de Ley de Potencia.

Licencia

Agregue un archivo de licencia antes de publicar el proyecto. Para una publicación pública como código abierto, las opciones comunes son MIT, BSD 3 Clause, Apache 2.0 o GPL 3.0, según qué tan permisivos desee que sean los términos de reutilización.