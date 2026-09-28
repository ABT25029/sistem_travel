# -*- coding: utf-8 -*-
"""
Sistema Inteligente Basado en Conocimiento para transporte intermunicipal
Corredor: Bogotá (Portal 80) - Villeta
"""

from typing import List, Dict, Optional

ESTACIONES = [
    "Portal 80", "Siberia", "La Punta", "Puente Piedra", "El Rosal",
    "El Vino", "San Francisco", "La Vega", "Nocaima", "Villeta"
]

RUTAS: Dict[str, List[str]] = {
    "Bogotá - Villeta": ["Portal 80", "Siberia", "La Punta", "Puente Piedra", "El Rosal", "El Vino", "San Francisco", "La Vega", "Nocaima", "Villeta"],
    "Villeta - Bogotá": ["Villeta", "Nocaima", "La Vega", "San Francisco", "El Vino", "El Rosal", "Puente Piedra", "La Punta", "Siberia", "Portal 80"],
}

PARADAS_TIQUETE: Dict[str, Dict[str, int]] = {
    "Bogotá - Villeta": {"El Rosal": 1, "La Vega": 1},
    "Villeta - Bogotá": {"Nocaima": 1, "La Vega": 1, "El Rosal": 1},
}
TIEMPO_TIQUETE = 10  # minutos por cada revisión de tiquete en municipios intermedios

TIEMPO_ACUMULADO: Dict[str, int] = {
    "Portal 80": 0, "Siberia": 20, "La Punta": 38, "Puente Piedra": 54,
    "El Rosal": 68, "El Vino": 80, "San Francisco": 90, "La Vega": 100,
    "Nocaima": 110, "Villeta": 120,
}


class MotorInferenciaViaje:
    """Agrupa las reglas lógicas que resuelven cómo ir de una estación a otra."""

    @staticmethod
    def regla_conexion_directa(estacion_origen: str, estacion_destino: str) -> List[Dict]:
        """Regla: SI origen y destino están en la misma ruta y en ese orden,
        ENTONCES puedes ir directo (sin trasbordo). El tiempo incluye las
        revisiones de tiquete de los municipios intermedios (no las del origen
        ni las del destino)."""
        opciones_directas = []
        for nombre_ruta, estaciones in RUTAS.items():
            if estacion_origen in estaciones and estacion_destino in estaciones:
                idx_orig = estaciones.index(estacion_origen)
                idx_dest = estaciones.index(estacion_destino)

                if idx_orig < idx_dest:
                    paradas = idx_dest - idx_orig  # intermedios + destino
                    tiempo_viaje = abs(TIEMPO_ACUMULADO[estacion_destino] - TIEMPO_ACUMULADO[estacion_origen])

                    # Regla de diseño: la revisión solo cuenta en municipios INTERMEDIOS
                    tramo = estaciones[idx_orig + 1:idx_dest]
                    tiquetes_ruta = PARADAS_TIQUETE.get(nombre_ruta, {})
                    tiquetes_en_tramo = {e: tiquetes_ruta[e] for e in tramo if e in tiquetes_ruta}
                    total_revisiones = sum(tiquetes_en_tramo.values())
                    tiempo_tiquetes = total_revisiones * TIEMPO_TIQUETE
                    tiempo = tiempo_viaje + tiempo_tiquetes

                    detalle = [f"Toma {nombre_ruta} desde '{estacion_origen}' hasta '{estacion_destino}' ({paradas} paradas)."]
                    if tiquetes_en_tramo:
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
        """Punto de entrada: valida las estaciones y devuelve la ruta directa
        más rápida entre origen y destino. Devuelve None si alguna estación
        no existe o si no hay ruta directa (no se manejan trasbordos)."""
        if origen not in ESTACIONES or destino not in ESTACIONES:
            print("[Regla] Alguna de las estaciones no existe en el sistema. No se puede inferir una ruta.")
            return None

        if origen == destino:
            print("[Regla] Origen y destino son la misma estación. No se necesita viajar.")
            return {"tipo": "Misma Estación", "trasbordos": 0, "paradas": 0, "tiempo_estimado": 0, "detalle": ["Ya te encuentras en la estación destino."]}

        # --- Paso 1: evaluar la regla de conexión directa (única regla disponible) ---
        print(f"[Regla] Evaluando SI existe una ruta directa entre '{origen}' y '{destino}'...")
        rutas_directas = cls.regla_conexion_directa(origen, destino)

        if rutas_directas:
            print(f"[Regla] SE CUMPLE: encontraste {len(rutas_directas)} opción(es) directa(s). Eliges la más rápida.")
            rutas_directas.sort(key=lambda x: (x["tiempo_estimado"], x["paradas"]))
            return rutas_directas[0]
        return None


def ejecutar_sistema():
    """Interfaz de consola: pide origen y destino y muestra la ruta calculada."""
    print("=" * 60)
    print(" SISTEMA BASADO EN CONOCIMIENTO: BOGOTÁ (PORTAL 80) - VILLETA")
    print("=" * 60)
    print("Estaciones disponibles en el sistema:")
    for idx, est in enumerate(ESTACIONES, 1):
        print(f" {idx}. {est}")
    print("-" * 60)

    try:
        idx_origen = int(input("Seleccione el número de la estación de ORIGEN (Punto A): ")) - 1
        idx_destino = int(input("Seleccione el número de la estación de DESTINO (Punto B): ")) - 1
        if not (0 <= idx_origen < len(ESTACIONES) and 0 <= idx_destino < len(ESTACIONES)):
            print("\n[Error] Selección inválida. Elija un número de la lista.")
            return

        origen = ESTACIONES[idx_origen]
        destino = ESTACIONES[idx_destino]
        print(f"\n[Calculando mejor ruta desde '{origen}' hasta '{destino}'...]\n")
        resultado = MotorInferenciaViaje.buscar_mejor_ruta(origen, destino)
        print("\n" + "=" * 60)
        print(" RESULTADO DE LA INFERENCIA LÓGICA")
        print("=" * 60)
        if resultado:
            print(f"Tipo de Ruta       : {resultado['tipo']}")
            print(f"Paradas            : {resultado['paradas']}")
            if resultado.get('paradas_tiquete'):
                print(f"Paradas de tiquete : {resultado['paradas_tiquete']}")
            print(f"Tiempo Estimado    : {resultado['tiempo_estimado']} minutos")
            print("\nInstrucciones de Viaje:")
            for paso in resultado["detalle"]:
                print(f" -> {paso}")
        else:
            print("No se encontró una ruta lógica válida para conectar los dos puntos seleccionados.")
    except ValueError:
        print("\n[Error] Debe ingresar únicamente números enteros.")


if __name__ == "__main__":
    ejecutar_sistema()
