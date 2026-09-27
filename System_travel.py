Sistema Inteligente Basado en Conocimiento para transporte intermunicipal
Corredor: Bogotá (Portal 80) - Villeta
Aquí modelas el conocimiento del dominio (hechos) y las reglas lógicas que
un motor de inferencia usa para decidir cómo ir de un punto a otro.
"""
 
from typing import List, Dict, Optional, Tuple
 
 
# 1. BASE DE CONOCIMIENTO (Hechos del Dominio)
# Acá guardas todo lo que el sistema "sabe" del mundo: municipios, rutas,
# tiempos y puntos de control. Las reglas de más abajo usan estos datos.
 
 
# Lista de todos los municipios/paradas válidas del corredor Bogotá - Villeta.
ESTACIONES = [
    "Portal 80", "Siberia", "La Punta", "Puente Piedra", "El Rosal",
    "El Vino", "San Francisco", "La Vega", "Nocaima", "Villeta"
]
 
# Cada ruta es una lista ordenada de paradas: define por dónde pasa y en qué
# sentido. El bus para en TODOS los municipios del corredor.
RUTAS: Dict[str, List[str]] = {
    "Bogotá - Villeta": ["Portal 80", "Siberia", "La Punta", "Puente Piedra", "El Rosal", "El Vino", "San Francisco", "La Vega", "Nocaima", "Villeta"],
    "Villeta - Bogotá": ["Villeta", "Nocaima", "La Vega", "San Francisco", "El Vino", "El Rosal", "Puente Piedra", "La Punta", "Siberia", "Portal 80"],
}
 
# Paradas de revisión de tiquetes: por cada ruta/sentido, tú defines un
# diccionario {municipio: cuántas revisiones de tiquete se hacen ahí}.
# Dependen de la ruta/sentido, suman tiempo extra, pero OJO: no cuentan
# como "paradas" de municipio. Ajusta los números si cambian los controles.
PARADAS_TIQUETE: Dict[str, Dict[str, int]] = {
    "Bogotá - Villeta": {"El Rosal": 1, "La Vega": 1},
    "Villeta - Bogotá": {"Nocaima": 1, "La Vega": 1, "El Rosal": 1},
}
TIEMPO_TIQUETE = 10  # minutos que le sumas al viaje por cada revisión de tiquete
 
# Tiempos acumulados (en minutos) desde Portal 80 hasta cada estación, medidos
# sobre el orden real del corredor Bogotá - Villeta (lista ESTACIONES).
# El recorrido completo Portal 80 -> Villeta dura siempre 120 minutos (2 horas).
# Los tramos van disminuyendo (20, 18, 16, 14, 12, 10, 10, 10, 10) porque tú
# asumes que la vía se vuelve más rápida (menos curvas, menor altura) entre
# más te acercas a Villeta.
TIEMPO_ACUMULADO: Dict[str, int] = {
    "Portal 80": 0,
    "Siberia": 20,
    "La Punta": 38,
    "Puente Piedra": 54,
    "El Rosal": 68,
    "El Vino": 80,
    "San Francisco": 90,
    "La Vega": 100,
    "Nocaima": 110,
    "Villeta": 120,
}
 
TIEMPO_TRASBORDO = 15  # minutos que penalizas por cambiarte de ruta (esperar el siguiente bus)
 
