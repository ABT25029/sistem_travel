# -*- coding: utf-8 -*-

"""
============================================================
SISTEMA INTELIGENTE BASADO EN CONOCIMIENTO
TRANSPORTE INTERMUNICIPAL
Corredor: Bogotá (Portal 80) - Villeta

Incluye:
1. Sistema basado en reglas para calcular la ruta y tiempo.
2. Aprendizaje supervisado para predecir tráfico.
3. Aprendizaje supervisado para estimar afectación climática.
4. Tiempo original + posible afectación por clima.
5. Aprendizaje supervisado para predecir demanda de pasajeros.
============================================================
"""

# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================

from typing import List, Dict, Optional
import random
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report


# ============================================================
# 2. BASE DE CONOCIMIENTO
# ============================================================

ESTACIONES = [
    "Portal 80",
    "Siberia",
    "La Punta",
    "Puente Piedra",
    "El Rosal",
    "El Vino",
    "San Francisco",
    "La Vega",
    "Nocaima",
    "Villeta"
]

# ------------------------------------------------------------
# RUTAS ORIGINALES
# ------------------------------------------------------------

RUTAS: Dict[str, List[str]] = {
    "Bogotá - Villeta": [
        "Portal 80",
        "Siberia",
        "La Punta",
        "Puente Piedra",
        "El Rosal",
        "El Vino",
        "San Francisco",
        "La Vega",
        "Nocaima",
        "Villeta"
    ],

    "Villeta - Bogotá": [
        "Villeta",
        "Nocaima",
        "La Vega",
        "San Francisco",
        "El Vino",
        "El Rosal",
        "Puente Piedra",
        "La Punta",
        "Siberia",
        "Portal 80"
    ],
}


# ------------------------------------------------------------
# PARADAS DE REVISIÓN DE TIQUETES
# ------------------------------------------------------------

PARADAS_TIQUETE: Dict[str, Dict[str, int]] = {
    "Bogotá - Villeta": {
        "El Rosal": 1,
        "La Vega": 1
    },

    "Villeta - Bogotá": {
        "Nocaima": 1,
        "La Vega": 1,
        "El Rosal": 1
    },
}

TIEMPO_TIQUETE = 10


# ------------------------------------------------------------
# TIEMPOS ACUMULADOS
# ------------------------------------------------------------

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

TIEMPO_TRASBORDO = 15


# ============================================================
# 3. MOTOR DE INFERENCIA
# ============================================================

class TransMi:

    """
    Agrupa las reglas lógicas que resuelven cómo
    ir de una estación a otra.
    """

    @staticmethod
    def regla_conexion_directa(
        estacion_origen: str,
        estacion_destino: str
    ) -> List[Dict]:

        opciones_directas = []

        # Recorremos las rutas existentes
        for nombre_ruta, estaciones in RUTAS.items():

            # Verificamos si ambas estaciones pertenecen a la ruta
            if (
                estacion_origen in estaciones
                and estacion_destino in estaciones
            ):

                idx_orig = estaciones.index(estacion_origen)
                idx_dest = estaciones.index(estacion_destino)

                # El origen debe estar antes del destino
                if idx_orig < idx_dest:

                    paradas = idx_dest - idx_orig

                    # Tiempo original del sistema
                    tiempo_viaje = abs(
                        TIEMPO_ACUMULADO[estacion_destino]
                        - TIEMPO_ACUMULADO[estacion_origen]
                    )

                    # Revisiones de tiquetes
                    tramo = estaciones[idx_orig + 1:idx_dest]

                    tiquetes_ruta = PARADAS_TIQUETE.get(
                        nombre_ruta,
                        {}
                    )

                    tiquetes_en_tramo = {
                        e: tiquetes_ruta[e]
                        for e in tramo
                        if e in tiquetes_ruta
                    }

                    total_revisiones = sum(
                        tiquetes_en_tramo.values()
                    )

                    tiempo_tiquetes = (
                        total_revisiones * TIEMPO_TIQUETE
                    )

                    # Tiempo original
                    tiempo = (
                        tiempo_viaje
                        + tiempo_tiquetes
                    )

                    # Detalle del viaje
                    detalle = [
                        f"Toma {nombre_ruta} desde "
                        f"'{estacion_origen}' hasta "
                        f"'{estacion_destino}' "
                        f"({paradas} paradas)."
                    ]

                    if tiquetes_en_tramo:

                        nombres = ", ".join(
                            f"'{e}' ({cant})"
                            for e, cant
                            in tiquetes_en_tramo.items()
                        )

                        detalle.append(
                            f"Incluye revisión de tiquetes "
                            f"en {nombres} "
                            f"(+{tiempo_tiquetes} min)."
                        )

                    opciones_directas.append({
                        "tipo": "Directa",
                        "ruta": nombre_ruta,
                        "trasbordos": 0,
                        "paradas": paradas,
                        "paradas_tiquete": total_revisiones,
                        "tiempo_estimado": tiempo,
                        "detalle": detalle
                    })

        return opciones_directas

    @classmethod
    def buscar_mejor_ruta(
        cls,
        origen: str,
        destino: str
    ) -> Optional[Dict]:

        # Validación
        if (
            origen not in ESTACIONES
            or destino not in ESTACIONES
        ):

            print(
                "[Regla] Alguna de las estaciones "
                "no existe en el sistema."
            )

            return None

        # Mismo punto
        if origen == destino:

            print(
                "[Regla] Origen y destino son "
                "la misma estación."
            )

            return {
                "tipo": "Misma Estación",
                "ruta": "Ninguna",
                "trasbordos": 0,
                "paradas": 0,
                "paradas_tiquete": 0,
                "tiempo_estimado": 0,
                "detalle": [
                    "Ya te encuentras en la estación destino."
                ]
            }

        # ----------------------------------------------------
        # REGLA DE CONEXIÓN DIRECTA
        # ----------------------------------------------------

        print(
            f"[Regla] Evaluando SI existe una ruta "
            f"directa entre '{origen}' y '{destino}'..."
        )

        rutas_directas = cls.regla_conexion_directa(
            origen,
            destino
        )

        if rutas_directas:

            print(
                f"[Regla] SE CUMPLE: "
                f"{len(rutas_directas)} opción(es) directa(s)."
            )

            rutas_directas.sort(
                key=lambda x: (
                    x["tiempo_estimado"],
                    x["paradas"]
                )
            )

            return rutas_directas[0]

        # ----------------------------------------------------
        # NO HAY RUTA DIRECTA
        # ----------------------------------------------------

        print(
            "[Regla] NO se encontró una conexión directa."
        )

        return None


# ============================================================
# 4. GENERACIÓN DEL DATASET DE TRÁFICO
# ============================================================

def generar_dataset_trafico(cantidad=800):

    datos = []

    dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo"
    ]

    rutas = list(RUTAS.keys())

    for _ in range(cantidad):

        hora = random.randint(5, 22)
        dia = random.choice(dias)
        ruta = random.choice(rutas)

        # ----------------------------------------------------
        # REGLAS SIMULADAS PARA CREAR EL TRÁFICO
        # ----------------------------------------------------

        puntaje = 0

        # Horas pico
        if hora in [7, 8, 9]:
            puntaje += 2

        elif hora in [17, 18, 19]:
            puntaje += 2

        elif hora in [10, 11, 12, 13, 14, 15, 16]:
            puntaje += 1

        # Fin de semana
        if dia in ["Sábado", "Domingo"]:
            puntaje -= 1

        # Viernes
        if dia == "Viernes":
            puntaje += 1

        # Ruta Bogotá - Villeta
        if ruta == "Bogotá - Villeta":
            puntaje += 1

        # Clasificación
        if puntaje >= 3:
            trafico = "Alto"

        elif puntaje >= 1:
            trafico = "Medio"

        else:
            trafico = "Bajo"

        datos.append({
            "hora": hora,
            "dia": dia,
            "ruta": ruta,
            "trafico": trafico
        })

    return pd.DataFrame(datos)


# ============================================================
# 5. PREPARACIÓN DEL MODELO DE TRÁFICO
# ============================================================

df_trafico = generar_dataset_trafico(800)

print("=" * 60)
print("DATASET DE TRÁFICO")
print("=" * 60)

display(df_trafico.head(20))

# ------------------------------------------------------------
# CONVERTIR VARIABLES CATEGÓRICAS
# ------------------------------------------------------------

encoder_dia_trafico = LabelEncoder()
encoder_ruta_trafico = LabelEncoder()
encoder_trafico = LabelEncoder()

df_trafico["dia_cod"] = (
    encoder_dia_trafico.fit_transform(
        df_trafico["dia"]
    )
)

df_trafico["ruta_cod"] = (
    encoder_ruta_trafico.fit_transform(
        df_trafico["ruta"]
    )
)

df_trafico["trafico_cod"] = (
    encoder_trafico.fit_transform(
        df_trafico["trafico"]
    )
)

# ------------------------------------------------------------
# VARIABLES DEL MODELO
# ------------------------------------------------------------

X_trafico = df_trafico[
    [
        "hora",
        "dia_cod",
        "ruta_cod"
    ]
]

y_trafico = df_trafico["trafico_cod"]

# ------------------------------------------------------------
# DIVISIÓN ENTRENAMIENTO / PRUEBA
# ------------------------------------------------------------

X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
    X_trafico,
    y_trafico,
    test_size=0.20,
    random_state=42,
    stratify=y_trafico
)

# ------------------------------------------------------------
# MODELO SUPERVISADO
# ------------------------------------------------------------

modelo_trafico = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

modelo_trafico.fit(
    X_train_t,
    y_train_t
)

# ------------------------------------------------------------
# EVALUACIÓN: SOLO PRECISIÓN
# ------------------------------------------------------------

predicciones_trafico = modelo_trafico.predict(
    X_test_t
)

reporte_trafico = classification_report(
    y_test_t,
    predicciones_trafico,
    target_names=encoder_trafico.classes_,
    output_dict=True,
    zero_division=0
)

print("\n")
print("=" * 60)
print("EVALUACIÓN DEL MODELO DE TRÁFICO")
print("=" * 60)

print("\nClase          Precisión")

for clase in encoder_trafico.classes_:

    precision = reporte_trafico[clase]["precision"]

    print(
        f"{clase:<15} {precision:.2f}"
    )


# ============================================================
# 6. GENERACIÓN DEL DATASET DE CLIMA
# ============================================================

def generar_dataset_clima(cantidad=800):

    datos = []

    dias = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo"
    ]

    rutas = list(RUTAS.keys())

    climas = [
        "Soleado",
        "Nublado",
        "Lluvia",
        "Tormenta",
        "Neblina"
    ]

    for _ in range(cantidad):

        hora = random.randint(5, 22)
        dia = random.choice(dias)
        ruta = random.choice(rutas)
        clima = random.choice(climas)

        # ----------------------------------------------------
        # REGLAS SIMULADAS DE AFECTACIÓN
        # ----------------------------------------------------

        puntaje = 0

        # Condición climática
        if clima == "Soleado":
            puntaje = 0

        elif clima == "Nublado":
            puntaje = 1

        elif clima == "Lluvia":
            puntaje = 2

        elif clima == "Tormenta":
            puntaje = 3

        elif clima == "Neblina":
            puntaje = 3

        # Horas de mayor circulación
        if hora in [7, 8, 9, 17, 18, 19]:
            puntaje += 1

        # Fin de semana
        if dia in ["Sábado", "Domingo"]:
            puntaje -= 1

        # ----------------------------------------------------
        # CLASIFICACIÓN
        # ----------------------------------------------------

        if puntaje <= 0:
            afectacion = "Sin impacto"

        elif puntaje <= 2:
            afectacion = "Impacto bajo"

        else:
            afectacion = "Impacto alto"

        datos.append({
            "hora": hora,
            "dia": dia,
            "ruta": ruta,
            "clima": clima,
            "afectacion": afectacion
        })

    return pd.DataFrame(datos)


# ============================================================
# 7. PREPARACIÓN DEL MODELO DE CLIMA
# ============================================================

df_clima = generar_dataset_clima(800)

print("\n")
print("=" * 60)
print("DATASET DE AFECTACIÓN CLIMÁTICA")
print("=" * 60)

display(df_clima.head(20))

# ------------------------------------------------------------
# ENCODERS
# ------------------------------------------------------------

encoder_dia_clima = LabelEncoder()
encoder_ruta_clima = LabelEncoder()
encoder_clima = LabelEncoder()
encoder_afectacion = LabelEncoder()

df_clima["dia_cod"] = (
    encoder_dia_clima.fit_transform(
        df_clima["dia"]
    )
)

df_clima["ruta_cod"] = (
    encoder_ruta_clima.fit_transform(
        df_clima["ruta"]
    )
)

df_clima["clima_cod"] = (
    encoder_clima.fit_transform(
        df_clima["clima"]
    )
)

df_clima["afectacion_cod"] = (
    encoder_afectacion.fit_transform(
        df_clima["afectacion"]
    )
)

# ------------------------------------------------------------
# VARIABLES DE ENTRADA
# ------------------------------------------------------------

X_clima = df_clima[
    [
        "hora",
        "dia_cod",
        "ruta_cod",
        "clima_cod"
    ]
]

y_clima = df_clima["afectacion_cod"]

# ------------------------------------------------------------
# DIVISIÓN
# ------------------------------------------------------------

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_clima,
    y_clima,
    test_size=0.20,
    random_state=42,
    stratify=y_clima
)

# ------------------------------------------------------------
# MODELO
# ------------------------------------------------------------

modelo_clima = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

modelo_clima.fit(
    X_train_c,
    y_train_c
)

# ------------------------------------------------------------
# EVALUACIÓN
# ------------------------------------------------------------

predicciones_clima = modelo_clima.predict(
    X_test_c
)

reporte_clima = classification_report(
    y_test_c,
    predicciones_clima,
    target_names=encoder_afectacion.classes_,
    output_dict=True,
    zero_division=0
)

print("\n")
print("=" * 60)
print("EVALUACIÓN DEL MODELO DE AFECTACIÓN CLIMÁTICA")
print("=" * 60)

print("\nClase             Precisión")

for clase in encoder_afectacion.classes_:

    precision = reporte_clima[clase]["precision"]

    print(
        f"{clase:<18} {precision:.2f}"
    )


# ============================================================
# 7A. GENERACIÓN DEL DATASET DE DEMANDA DE PASAJEROS
# ============================================================

def generar_dataset_demanda(cantidad=800):
    """Genera datos simulados para clasificar la demanda de pasajeros.

    IMPORTANTE: las etiquetas se crean mediante reglas artificiales.
    Para uso real, deben reemplazarse por conteos históricos de pasajeros.
    """

    datos = []

    dias = [
        "Lunes", "Martes", "Miércoles", "Jueves",
        "Viernes", "Sábado", "Domingo"
    ]

    rutas = list(RUTAS.keys())

    for _ in range(cantidad):

        hora = random.randint(5, 22)
        dia = random.choice(dias)
        ruta = random.choice(rutas)

        puntaje = 0

        # Horas habituales de mayor demanda
        if hora in [6, 7, 8, 9, 17, 18, 19]:
            puntaje += 2

        elif hora in [10, 11, 12, 13, 14, 15, 16]:
            puntaje += 1

        # Viernes puede aumentar la demanda de viajes intermunicipales
        if dia == "Viernes":
            puntaje += 1

        # En este ejemplo se supone una demanda algo mayor hacia Villeta
        if ruta == "Bogotá - Villeta":
            puntaje += 1

        # Se aplica una reducción simulada durante el fin de semana.
        # Es una regla ilustrativa, no una conclusión basada en datos reales.
        if dia == "Domingo":
            puntaje -= 1

        if puntaje >= 3:
            demanda = "Alta"

        elif puntaje >= 1:
            demanda = "Media"

        else:
            demanda = "Baja"

        datos.append({
            "hora": hora,
            "dia": dia,
            "ruta": ruta,
            "demanda": demanda
        })

    return pd.DataFrame(datos)


# ============================================================
# 7B. PREPARACIÓN Y ENTRENAMIENTO DEL MODELO DE DEMANDA
# ============================================================

df_demanda = generar_dataset_demanda(800)

print("\n")
print("=" * 60)
print("DATASET DE DEMANDA DE PASAJEROS")
print("=" * 60)

display(df_demanda.head(20))

encoder_dia_demanda = LabelEncoder()
encoder_ruta_demanda = LabelEncoder()
encoder_demanda = LabelEncoder()

df_demanda["dia_cod"] = (
    encoder_dia_demanda.fit_transform(
        df_demanda["dia"]
    )
)

df_demanda["ruta_cod"] = (
    encoder_ruta_demanda.fit_transform(
        df_demanda["ruta"]
    )
)

df_demanda["demanda_cod"] = (
    encoder_demanda.fit_transform(
        df_demanda["demanda"]
    )
)

X_demanda = df_demanda[
    [
        "hora",
        "dia_cod",
        "ruta_cod"
    ]
]

y_demanda = df_demanda["demanda_cod"]

X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
    X_demanda,
    y_demanda,
    test_size=0.20,
    random_state=42,
    stratify=y_demanda
)

modelo_demanda = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

modelo_demanda.fit(
    X_train_d,
    y_train_d
)

predicciones_demanda = modelo_demanda.predict(
    X_test_d
)

reporte_demanda = classification_report(
    y_test_d,
    predicciones_demanda,
    target_names=encoder_demanda.classes_,
    output_dict=True,
    zero_division=0
)

print("\n")
print("=" * 60)
print("EVALUACIÓN DEL MODELO DE DEMANDA")
print("=" * 60)

print("\nClase             Precisión")

for clase in encoder_demanda.classes_:

    precision = reporte_demanda[clase]["precision"]

    print(
        f"{clase:<18} {precision:.2f}"
    )


# ============================================================
# 8. FUNCIONES PARA PREDECIR TRÁFICO
# ============================================================

def predecir_trafico(
    hora,
    dia,
    ruta
):

    dia_cod = encoder_dia_trafico.transform(
        [dia]
    )[0]

    ruta_cod = encoder_ruta_trafico.transform(
        [ruta]
    )[0]

    datos = pd.DataFrame({
        "hora": [hora],
        "dia_cod": [dia_cod],
        "ruta_cod": [ruta_cod]
    })

    prediccion = modelo_trafico.predict(
        datos
    )[0]

    trafico = encoder_trafico.inverse_transform(
        [prediccion]
    )[0]

    return trafico


# ============================================================
# 9. FUNCIÓN PARA PREDECIR AFECTACIÓN CLIMÁTICA
# ============================================================

def predecir_afectacion_clima(
    hora,
    dia,
    ruta,
    clima
):

    dia_cod = encoder_dia_clima.transform(
        [dia]
    )[0]

    ruta_cod = encoder_ruta_clima.transform(
        [ruta]
    )[0]

    clima_cod = encoder_clima.transform(
        [clima]
    )[0]

    datos = pd.DataFrame({
        "hora": [hora],
        "dia_cod": [dia_cod],
        "ruta_cod": [ruta_cod],
        "clima_cod": [clima_cod]
    })

    prediccion = modelo_clima.predict(
        datos
    )[0]

    afectacion = (
        encoder_afectacion.inverse_transform(
            [prediccion]
        )[0]
    )

    return afectacion


# ============================================================
# 9A. FUNCIÓN PARA PREDECIR LA DEMANDA DE PASAJEROS
# ============================================================

def predecir_demanda(hora, dia, ruta):
    """Predice la demanda simulada: Baja, Media o Alta."""

    dia_cod = encoder_dia_demanda.transform(
        [dia]
    )[0]

    ruta_cod = encoder_ruta_demanda.transform(
        [ruta]
    )[0]

    datos = pd.DataFrame({
        "hora": [hora],
        "dia_cod": [dia_cod],
        "ruta_cod": [ruta_cod]
    })

    prediccion = modelo_demanda.predict(
        datos
    )[0]

    demanda = encoder_demanda.inverse_transform(
        [prediccion]
    )[0]

    return demanda


# ============================================================
# 10. AJUSTE DEL TIEMPO SEGÚN AFECTACIÓN CLIMÁTICA
# ============================================================

def calcular_tiempo_clima(
    tiempo_original,
    afectacion
):

    # IMPORTANTE:
    # El modelo NO cambia el tiempo original.
    #
    # Solamente calculamos una estimación adicional
    # debido a la posible afectación climática.

    incrementos = {
        "Sin impacto": 0,
        "Impacto bajo": 10,
        "Impacto alto": 20
    }

    incremento = incrementos.get(
        afectacion,
        0
    )

    tiempo_con_clima = (
        tiempo_original
        + incremento
    )

    return incremento, tiempo_con_clima


# ============================================================
# 11. INTERFAZ PRINCIPAL
# ============================================================

def ejecutar_sistema():

    print("\n")
    print("=" * 70)

    print(
        " SISTEMA INTELIGENTE DE TRANSPORTE"
    )

    print(
        " BOGOTÁ (PORTAL 80) - VILLETA"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # ESTACIONES
    # --------------------------------------------------------

    print("\nEstaciones disponibles:\n")

    for idx, estacion in enumerate(
        ESTACIONES,
        1
    ):

        print(
            f" {idx}. {estacion}"
        )

    print("-" * 70)

    try:

        # ----------------------------------------------------
        # ORIGEN
        # ----------------------------------------------------

        idx_origen = int(
            input(
                "\nSeleccione el número "
                "de la estación de ORIGEN: "
            )
        ) - 1

        # ----------------------------------------------------
        # DESTINO
        # ----------------------------------------------------

        idx_destino = int(
            input(
                "Seleccione el número "
                "de la estación de DESTINO: "
            )
        ) - 1

        # Validación
        if not (
            0 <= idx_origen < len(ESTACIONES)
            and
            0 <= idx_destino < len(ESTACIONES)
        ):

            print(
                "\n[Error] Selección inválida."
            )

            return

        origen = ESTACIONES[
            idx_origen
        ]

        destino = ESTACIONES[
            idx_destino
        ]

        # ----------------------------------------------------
        # HORA
        # ----------------------------------------------------

        hora = int(
            input(
                "\nIngrese la hora del viaje "
                "(5 - 22): "
            )
        )

        if hora < 5 or hora > 22:

            print(
                "\n[Error] La hora debe "
                "estar entre 5 y 22."
            )

            return

        # ----------------------------------------------------
        # DÍA
        # ----------------------------------------------------

        print("\nDías disponibles:")

        dias = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"
        ]

        for idx, dia in enumerate(
            dias,
            1
        ):

            print(
                f" {idx}. {dia}"
            )

        idx_dia = int(
            input(
                "\nSeleccione el número "
                "del día: "
            )
        ) - 1

        if not (
            0 <= idx_dia < len(dias)
        ):

            print(
                "\n[Error] Día inválido."
            )

            return

        dia = dias[idx_dia]

        # ----------------------------------------------------
        # CLIMA
        # ----------------------------------------------------

        print("\nCondiciones climáticas:")

        climas = [
            "Soleado",
            "Nublado",
            "Lluvia",
            "Tormenta",
            "Neblina"
        ]

        for idx, clima in enumerate(
            climas,
            1
        ):

            print(
                f" {idx}. {clima}"
            )

        idx_clima = int(
            input(
                "\nSeleccione el número "
                "del clima: "
            )
        ) - 1

        if not (
            0 <= idx_clima < len(climas)
        ):

            print(
                "\n[Error] Condición climática inválida."
            )

            return

        clima = climas[idx_clima]

        # ====================================================
        # MOTOR DE INFERENCIA
        # ====================================================

        print("\n")
        print("=" * 70)
        print("PROCESANDO INFORMACIÓN...")
        print("=" * 70)

        resultado = (
            TransMi.buscar_mejor_ruta(
                origen,
                destino
            )
        )

        if not resultado:

            print(
                "\nNo se encontró una "
                "ruta válida."
            )

            return

        # ====================================================
        # RUTA VÁLIDA
        # ====================================================

        ruta = resultado.get(
            "ruta"
        )

        # ====================================================
        # MODELO DE TRÁFICO
        # ====================================================

        trafico = predecir_trafico(
            hora,
            dia,
            ruta
        )

        # ====================================================
        # MODELO DE CLIMA
        # ====================================================

        afectacion = (
            predecir_afectacion_clima(
                hora,
                dia,
                ruta,
                clima
            )
        )

        # ====================================================
        # MODELO DE DEMANDA DE PASAJEROS (NUEVO)
        # ====================================================

        demanda = predecir_demanda(
            hora,
            dia,
            ruta
        )

        # ====================================================
        # TIEMPO ORIGINAL + CLIMA
        # ====================================================

        tiempo_original = (
            resultado[
                "tiempo_estimado"
            ]
        )

        incremento, tiempo_con_clima = (
            calcular_tiempo_clima(
                tiempo_original,
                afectacion
            )
        )

        # ====================================================
        # RESULTADO FINAL
        # ====================================================

        print("\n")
        print("=" * 70)
        print(" RESULTADO DEL SISTEMA")
        print("=" * 70)

        print(
            f"Punto A                 : {origen}"
        )

        print(
            f"Punto B                 : {destino}"
        )

        print(
            f"Hora                    : {hora}:00"
        )

        print(
            f"Día                     : {dia}"
        )

        print(
            f"Condición climática     : {clima}"
        )

        print("\n")
        print("-" * 70)
        print("RESULTADO DE LA INFERENCIA LÓGICA")
        print("-" * 70)

        print(
            f"Ruta                    : {ruta}"
        )

        print(
            f"Tipo de Ruta            : {resultado['tipo']}"
        )

        print(
            f"Paradas                 : {resultado['paradas']}"
        )

        print(
            f"Paradas de tiquete      : "
            f"{resultado.get('paradas_tiquete', 0)}"
        )

        print(
            f"Tiempo Original         : "
            f"{tiempo_original} minutos"
        )


        print("\n" + "-" * 70)
        print("APRENDIZAJE SUPERVISADO")
        print("-" * 70)
        print(f"Tráfico previsto        : {trafico}")
        print(f"Afectación climática    : {afectacion}")

        print("\n" + "-" * 70)
        print("APRENDIZAJE AUTOMÁTICO")
        print("-" * 70)
        print(f"Demanda de pasajeros    : {demanda}")


        print("\n")
        print("-" * 70)
        print("ESTIMACIÓN DEL TIEMPO CON CLIMA")
        print("-" * 70)

        print(
            f"Tiempo original         : "
            f"{tiempo_original} minutos"
        )

        print(
            f"Incremento por clima    : "
            f"+{incremento} minutos"
        )

        print(
            f"Tiempo con clima        : "
            f"{tiempo_con_clima} minutos"
        )

        print("\n")
        print("-" * 70)
        print("INSTRUCCIONES DE VIAJE")
        print("-" * 70)

        for paso in resultado["detalle"]:

            print(
                f" -> {paso}"
            )

        print("\n")
        print("=" * 70)
        print(" FIN DEL RESULTADO")
        print("=" * 70)

    except ValueError:

        print(
            "\n[Error] Debe ingresar "
            "únicamente números."
        )


# ============================================================
# 12. EJECUTAR SISTEMA
# ============================================================

ejecutar_sistema()
