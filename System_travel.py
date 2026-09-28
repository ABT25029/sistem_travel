# -*- coding: utf-8 -*-
"""
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

# Paradas de revisión de tiquetes: por cada ruta/sentido, se define un
# diccionario {municipio: cuántas revisiones de tiquete se hacen ahí}.
# Dependen de la ruta/sentido, suman tiempo extra
PARADAS_TIQUETE: Dict[str, Dict[str, int]] = {
    "Bogotá - Villeta": {"El Rosal": 1, "La Vega": 1},
    "Villeta - Bogotá": {"Nocaima": 1, "La Vega": 1, "El Rosal": 1},
}
TIEMPO_TIQUETE = 10  # minutos que le sumas al viaje por cada revisión de tiquete

# Tiempos acumulados (en minutos) desde Portal 80 hasta cada estación, medidos
# sobre el orden real del corredor Bogotá - Villeta (lista ESTACIONES).
# El recorrido completo Portal 80 -> Villeta dura siempre 120 minutos (2 horas).
# Los tramos van disminuyendo (20, 18, 16, 14, 12, 10, 10, 10, 10) 
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

TIEMPO_TRASBORDO = 15  # minutos para cambiarte de ruta (esperar el siguiente bus)



# 2. MOTOR DE INFERENCIA Y REGLAS LÓGICAS
# Cada método "regla_..." es una regla del tipo SI (condición) ENTONCES
# (conclusión), igual que los if/elif del ejemplo de clase, solo que aquí
# se evalúa recorriendo los datos en vez de escribir uno por uno


class MotorInferenciaViaje:
    """Agrupa las reglas lógicas que resuelven cómo ir de una estación a otra."""

    @staticmethod
    def regla_conexion_directa(estacion_origen: str, estacion_destino: str) -> List[Dict]:
        """Regla: SI origen y destino están en la misma ruta y en ese orden,
        ENTONCES puedes ir directo (sin trasbordo)."""
        opciones_directas = []
        for nombre_ruta, estaciones in RUTAS.items():  # Revisas cada ruta que tienes en la base de conocimiento
            if estacion_origen in estaciones and estacion_destino in estaciones:  # ¿La ruta toca ambos puntos?
                idx_orig = estaciones.index(estacion_origen)
                idx_dest = estaciones.index(estacion_destino)

                if idx_orig < idx_dest:  # El origen debe ir ANTES que el destino en esa ruta; si no, no aplica
                    paradas = idx_dest - idx_orig  # Cuántos municipios hay entre origen y destino
                    tiempo_viaje = abs(TIEMPO_ACUMULADO[estacion_destino] - TIEMPO_ACUMULADO[estacion_origen])  # Tiempo puro de viaje (sin tiquetes)

                    # Ahora calculas si en el camino hay revisiones de tiquete
                    tramo = estaciones[idx_orig + 1:idx_dest]  # Municipios intermedios (sin contar origen ni destino)
                    tiquetes_ruta = PARADAS_TIQUETE.get(nombre_ruta, {})  # Diccionario de revisiones de esta ruta
                    tiquetes_en_tramo = {e: tiquetes_ruta[e] for e in tramo if e in tiquetes_ruta}  # Solo los que caen en el tramo
                    total_revisiones = sum(tiquetes_en_tramo.values())  # Suma de revisiones (puede haber más de 1 por municipio)
                    tiempo_tiquetes = total_revisiones * TIEMPO_TIQUETE  # Minutos extra por  revision
                    tiempo = tiempo_viaje + tiempo_tiquetes  # Tiempo total: viaje + revisiones

                    detalle = [f"Toma {nombre_ruta} desde '{estacion_origen}' hasta '{estacion_destino}' ({paradas} paradas)."]
                    if tiquetes_en_tramo:  # Si hubo revisiones en el camino, las explicas aparte
                        nombres = ", ".join(f"'{e}' ({cant})" for e, cant in tiquetes_en_tramo.items())
                        detalle.append(f"Incluye revisión de tiquetes en {nombres} (+{tiempo_tiquetes} min).")

                    opciones_directas.append({
                        "tipo": "Directa",
                        "trasbordos": 0,
                        "paradas": paradas,
                        "paradas_tiquete": total_revisiones,
                        "tiempo_estimado": tiempo,
                        "detalle": detalle
                    })
        return opciones_directas

 
    @classmethod
    def buscar_mejor_ruta(cls, origen: str, destino: str) -> Optional[Dict]:
        """Punto de entrada: validas las estaciones y devuelves la ruta más
        rápida, evaluando primero la regla directa y luego la de trasbordo
        (igual que encadenas if/elif/else en el ejemplo de clase)."""
        if origen not in ESTACIONES or destino not in ESTACIONES:  # Validas que ambos puntos existan en tu base de conocimiento
            print("[Regla] Alguna de las estaciones no existe en el sistema. No se puede inferir una ruta.")
            return None

        if origen == destino:  # Caso trivial: ya llegaste
            print("[Regla] Origen y destino son la misma estación. No se necesita viajar.")
            return {"tipo": "Misma Estación", "trasbordos": 0, "paradas": 0, "tiempo_estimado": 0, "detalle": ["Ya te encuentras en la estación destino."]}

        # --- Paso 1: evalua la regla de conexión directa ---
        print(f"[Regla] Evaluando SI existe una ruta directa entre '{origen}' y '{destino}'...")
        rutas_directas = cls.regla_conexion_directa(origen, destino)

        if rutas_directas:
            print(f"[Regla] SE CUMPLE: encontraste {len(rutas_directas)} opción(es) directa(s). Eliges la más rápida.")
            # Si empatan en tiempo, prefieres la de menos paradas (más cómoda para el pasajero)
            rutas_directas.sort(key=lambda x: (x["tiempo_estimado"], x["paradas"]))
            return rutas_directas[0]

  



# 3. INTERFAZ DE USUARIO Y PRUEBAS EN CONSOLA
# Acá se pide al usuario origen y destino, y le muestras cómo el motor de
# inferencia fue evaluando las reglas hasta llegar al resultado.


def ejecutar_sistema():
    """Interfaz de consola: pides origen y destino, y muestras la ruta calculada."""
    print("=" * 60)
    print(" SISTEMA BASADO EN CONOCIMIENTO: BOGOTÁ (PORTAL 80) - VILLETA")
    print("=" * 60)
    print("Estaciones disponibles en el sistema:")
    for idx, est in enumerate(ESTACIONES, 1):  # se muestra al usuario la lista numerada para que elija
        print(f" {idx}. {est}")
    print("-" * 60)

    try:
        idx_origen = int(input("Seleccione el número de la estación de ORIGEN (Punto A): ")) - 1
        idx_destino = int(input("Seleccione el número de la estación de DESTINO (Punto B): ")) - 1
        if not (0 <= idx_origen < len(ESTACIONES) and 0 <= idx_destino < len(ESTACIONES)):  # Validas que el número elegido exista en la lista
            print("\n[Error] Selección inválida. Elija un número de la lista.")
            return

        origen = ESTACIONES[idx_origen]
        destino = ESTACIONES[idx_destino]
        print(f"\n[Calculando mejor ruta desde '{origen}' hasta '{destino}'...]\n")
        resultado = MotorInferenciaViaje.buscar_mejor_ruta(origen, destino)  # Aquí se dispara todo el razonamiento del motor
        print("\n" + "=" * 60)
        print(" RESULTADO DE LA INFERENCIA LÓGICA")
        print("=" * 60)
        if resultado:  # Si el motor sí encontró una ruta, la muestras completa
            print(f"Tipo de Ruta       : {resultado['tipo']}")
            print(f"Paradas            : {resultado['paradas']}")
            if resultado.get('paradas_tiquete'):  # Solo la muestras si hubo revisiones de tiquete
                print(f"Paradas de tiquete : {resultado['paradas_tiquete']}")
            print(f"Tiempo Estimado    : {resultado['tiempo_estimado']} minutos")
            print("\nInstrucciones de Viaje:")
            for paso in resultado["detalle"]:
                print(f" -> {paso}")
        else:  # Si no, le avisas al usuario que no hubo forma de conectar los puntos
            print("No se encontró una ruta lógica válida para conectar los dos puntos seleccionados.")
    except ValueError:  # Si el usuario escribe algo que no es un número
        print("\n[Error] Debe ingresar únicamente números enteros.")

if __name__ == "__main__":
    ejecutar_sistema()
