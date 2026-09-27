Sistema Inteligente de Rutas Bogotá - Villeta

Descripción del proyecto

Este proyecto es un sistema basado en conocimiento desarrollado en Python. Su función principal es encontrar una ruta entre diferentes puntos del corredor Bogotá (Portal 80) - Villeta.

El programa cuenta con una base de conocimiento donde se encuentran las estaciones, las rutas disponibles, los tiempos de recorrido y algunos puntos donde se realizan revisiones de tiquetes.

Para encontrar una ruta, el sistema utiliza un motor de inferencia que aplica diferentes reglas. Primero revisa si existe una conexión directa entre el punto de origen y el destino. Si no encuentra una conexión directa, busca la posibilidad de realizar un trasbordo en otra estación.

El tiempo estimado del recorrido tiene en cuenta el tiempo de viaje entre las estaciones, las revisiones de tiquetes y el tiempo adicional que se considera para realizar un trasbordo.

Al ejecutar el programa, el usuario debe seleccionar una estación de origen y una estación de destino. Después de esto, el sistema analiza las opciones disponibles y muestra en la consola la ruta encontrada, el número de paradas y el tiempo estimado del recorrido.

Las estaciones que se manejan en el sistema son:

   -Portal 80
    
   -Siberia
    
   -La Punta
    
   -Puente Piedra
    
   -El Rosal
    
   -El Vino
    
   -San Francisco
    
   -La Vega
    
   -Nocaima
    
   -Villeta

Requisitos previos

Para ejecutar el proyecto se necesita tener instalado Python.

Python

Se recomienda utilizar Python 3.8 o una versión superior.

Para comprobar la versión instalada se puede ejecutar:

python --version

En algunos sistemas también puede ser necesario utilizar:

python3 --version

Sistema operativo

El proyecto puede ejecutarse en sistemas operativos que tengan soporte para Python, como:

  -Windows

  -Linux

  -macOS

Librerías

El proyecto utiliza librerías que hacen parte de Python y no necesita instalar paquetes externos adicionales.

Entre las librerías utilizadas está typing, que se utiliza para definir los tipos de datos empleados en el código:

from typing import List, Dict, Optional, Tuple

Editor o terminal

Se puede ejecutar el proyecto desde una terminal o desde un editor de código como Visual Studio Code, PyCharm o cualquier otro entorno que permita ejecutar archivos de Python.

Ejecución

Una vez descargado o clonado el proyecto, se debe abrir una terminal en la carpeta donde se encuentra el archivo Python y ejecutar:

python nombre_del_archivo.py

El programa mostrará las estaciones disponibles y solicitará seleccionar el punto de origen y el punto de destino.

Después de realizar la selección, el sistema ejecutará las reglas de inferencia y mostrará el resultado en la consola.
