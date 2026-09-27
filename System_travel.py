"""Sistema Inteligente Basado en Conocimiento para transporte intermunicipal
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
 # ============================================================
# 2. MOTOR DE INFERENCIA Y REGLAS LÓGICAS
# Cada método "regla_..." representa una regla del tipo SI (condición)
# ENTONCES (conclusión) — el mismo principio de los if/elif del ejemplo de
# clase, solo que aquí las reglas se evalúan recorriendo datos en vez de
# escribirse una por una a mano.
# ============================================================

class MotorInferenciaTransMilenio:
    """Agrupa las reglas lógicas que resuelven cómo ir de una estación a otra."""

    @staticmethod
    def regla_conexion_directa(estacion_origen: str, estacion_destino: str) -> List[Dict]:
        """
        Regla 1 (conexión directa):
        SI el origen y el destino están en la misma ruta, y el origen aparece
        ANTES que el destino en esa ruta,
        ENTONCES existe un viaje directo (sin trasbordo) entre ambos.
        """
        opciones_directas = []

        # Revisas una por una todas las rutas que existen en la base de conocimiento
        for nombre_ruta, estaciones in RUTAS.items():

            # Primer chequeo de la regla: ¿esta ruta pasa por los dos puntos?
            if estacion_origen in estaciones and estacion_destino in estaciones:
                idx_orig = estaciones.index(estacion_origen)  # Posición del origen dentro de esta ruta
                idx_dest = estaciones.index(estacion_destino)  # Posición del destino dentro de esta ruta

                # Segundo chequeo de la regla: el origen debe ir ANTES que el
                # destino; si no, esta ruta no sirve en este sentido
                if idx_orig < idx_dest:
                    paradas = idx_dest - idx_orig  # Cantidad de municipios entre origen y destino

                    # Tiempo puro de viaje (sin contar revisiones de tiquete),
                    # calculado como la diferencia de tiempos acumulados
                    tiempo_viaje = abs(TIEMPO_ACUMULADO[estacion_destino] - TIEMPO_ACUMULADO[estacion_origen])

                    # Ahora revisas si en el camino hay revisiones de tiquete que sumen tiempo
                    tramo = estaciones[idx_orig + 1:idx_dest]  # Municipios intermedios, sin contar origen ni destino
                    tiquetes_ruta = PARADAS_TIQUETE.get(nombre_ruta, {})  # Diccionario de revisiones de esta ruta
                    tiquetes_en_tramo = {e: tiquetes_ruta[e] for e in tramo if e in tiquetes_ruta}  # Solo los que caen dentro del tramo
                    total_revisiones = sum(tiquetes_en_tramo.values())  # Suma de revisiones (puede haber más de una por municipio)
                    tiempo_tiquetes = total_revisiones * TIEMPO_TIQUETE  # Minutos extra por esas revisiones
                    tiempo = tiempo_viaje + tiempo_tiquetes  # Tiempo total: viaje + revisiones de tiquete

                    # Armas el mensaje explicando el viaje, paso a paso
                    detalle = [f"Toma {nombre_ruta} desde '{estacion_origen}' hasta '{estacion_destino}' ({paradas} paradas)."]
                    if tiquetes_en_tramo:  # Solo agregas esta línea si de verdad hubo revisiones en el camino
                        nombres = ", ".join(f"'{e}' ({cant})" for e, cant in tiquetes_en_tramo.items())
                        detalle.append(f"Incluye revisión de tiquetes en {nombres} (+{tiempo_tiquetes} min).")

                    # Guardas esta opción de viaje directo con toda su información
                    opciones_directas.append({
                        "tipo": "Directa",
                        "trasbordos": 0,
                        "paradas": paradas,
                        "paradas_tiquete": total_revisiones,
                        "tiempo_estimado": tiempo,
                        "detalle": detalle
                    })

        return opciones_directas

    @staticmethod
    def regla_conexion_trasbordo(estacion_origen: str, estacion_destino: str) -> List[Dict]:
        """
        Regla 2 (conexión con trasbordo):
        SI no existe una ruta directa entre origen y destino,
        ENTONCES buscas un municipio intermedio que sí conecte con ambos por
        separado, para armar el viaje en dos tramos con un trasbordo.
        """
        opciones_trasbordo = []

        # Pruebas cada municipio del corredor como posible punto de trasbordo
        for estacion_intermedia in ESTACIONES:

            # No tiene sentido "trasbordar" justo en el origen o en el destino
            if estacion_intermedia in (estacion_origen, estacion_destino):
                continue

            # Tramo 1: origen -> estación intermedia (usando la Regla 1)
            trayectos_1 = MotorInferenciaTransMilenio.regla_conexion_directa(estacion_origen, estacion_intermedia)
            # Tramo 2: estación intermedia -> destino (usando la Regla 1)
            trayectos_2 = MotorInferenciaTransMilenio.regla_conexion_directa(estacion_intermedia, estacion_destino)

            # Combinas cada opción del tramo 1 con cada opción del tramo 2
            for t1 in trayectos_1:
                for t2 in trayectos_2:
                    # El tiempo total suma los dos tramos más la espera del trasbordo
                    tiempo_total = t1["tiempo_estimado"] + t2["tiempo_estimado"] + TIEMPO_TRASBORDO
                    opciones_trasbordo.append({
                        "tipo": "Con Trasbordo",
                        "trasbordos": 1,
                        "paradas": t1["paradas"] + t2["paradas"],
                        "tiempo_estimado": tiempo_total,
                        "estacion_trasbordo": estacion_intermedia,
                        "detalle": [
                            t1["detalle"][0],
                            f"Haz trasbordo en '{estacion_intermedia}' (tiempo estimado trasbordo: {TIEMPO_TRASBORDO} min).",
                            t2["detalle"][0]
                        ]
                    })

        return opciones_trasbordo

    @classmethod
    def buscar_mejor_ruta(cls, origen: str, destino: str) -> Optional[Dict]:
        """
        Punto de entrada del motor de inferencia: valida las estaciones y
        devuelve la ruta más rápida, evaluando primero la Regla 1 (directa)
        y, si no aplica, la Regla 2 (trasbordo) — igual que encadenas
        if/elif/else en el ejemplo de clase.
        """
        # Validación: ambas estaciones deben existir en la base de conocimiento
        if origen not in ESTACIONES or destino not in ESTACIONES:
            print("[Regla] Alguna de las estaciones no existe en el sistema. No se puede inferir una ruta.")
            return None

        # Caso trivial: origen y destino son el mismo punto
        if origen == destino:
            print("[Regla] Origen y destino son la misma estación. No se necesita viajar.")
            return {"tipo": "Misma Estación", "trasbordos": 0, "paradas": 0, "tiempo_estimado": 0, "detalle": ["Ya te encuentras en la estación destino."]}

        # --- Paso 1: evalúas la Regla 1 (conexión directa) ---
        print(f"[Regla] Evaluando SI existe una ruta directa entre '{origen}' y '{destino}'...")
        rutas_directas = cls.regla_conexion_directa(origen, destino)

        if rutas_directas:
            print(f"[Regla] SE CUMPLE: encontraste {len(rutas_directas)} opción(es) directa(s). Eliges la más rápida.")
            # Si dos opciones empatan en tiempo, gana la que tenga menos paradas
            # (más cómoda para el pasajero)
            rutas_directas.sort(key=lambda x: (x["tiempo_estimado"], x["paradas"]))
            return rutas_directas[0]

        # --- Paso 2: si la Regla 1 no aplicó, evalúas la Regla 2 (trasbordo) ---
        print("[Regla] NO se cumple la conexión directa. Evaluando SI es posible con un trasbordo...")
        rutas_trasbordo = cls.regla_conexion_trasbordo(origen, destino)
        if rutas_trasbordo:
            print(f"[Regla] SE CUMPLE: encontraste {len(rutas_trasbordo)} opción(es) con trasbordo. Eliges la más rápida.")
            rutas_trasbordo.sort(key=lambda x: (x["tiempo_estimado"], x["paradas"]))
            return rutas_trasbordo[0]

        # Ninguna regla aplicó: no hay forma de conectar esos dos puntos
        print("[Regla] NO se cumple ninguna regla. No hay conexión posible entre esos dos puntos.")
        return None

# 3. INTERFAZ DE USUARIO Y PRUEBAS EN CONSOLA
# Acá le pides al usuario origen y destino, y le muestras cómo el motor de
# inferencia fue evaluando las reglas hasta llegar al resultado.


def ejecutar_sistema():
    """Interfaz de consola: pides origen y destino, y muestras la ruta calculada."""
    print("=" * 60)
    print(" SISTEMA BASADO EN CONOCIMIENTO: BOGOTÁ (PORTAL 80) - VILLETA")
    print("=" * 60)
    print("Estaciones disponibles en el sistema:")
    for idx, est in enumerate(ESTACIONES, 1):  # Le muestras al usuario la lista numerada para que elija
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
        resultado = MotorInferenciaTransMilenio.buscar_mejor_ruta(origen, destino)  # Aquí se dispara todo el razonamiento del motor
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
