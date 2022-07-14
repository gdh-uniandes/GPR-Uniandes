# GPR-Uniandes

Proyecto Desminado Humanitario para la detección de explosivos con el uso de un GPR. Este repositorio es un resumen del proyecto Desminado Humanitario desarrollado en los repositorios [https://gitlab.com/desminadohumanitariouniandes](https://gitlab.com/desminadohumanitariouniandes). Para conocer rápidamente cómo poner en marcha el GPR, tomar muestras y graficarlas se recomienda revisar el [manual de primer uso del GPR](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/manuales/Manual_Primer_Uso.pdf). Se recomienda también revisar cada sección a continuación.


## Instalación

La instalación de las dependencias de Python se ejecuta con el siguiente comando.

```
pip install -r requirements.txt
```

Adicionalmente se requiere instalar una librería para el manejo del protocolo VXI-11 en Python:

* [python-vxi11](https://github.com/python-ivi/python-vxi11) - Driver VXI-11 para el control en Python de instrumentos vía Ethernet (Revisar la instalación).

## Programas

El manejo de los GPR se lleva a cabo con los programas en las carpetas [GPR-V2](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/GPR-V2) y [GPR-V2 - Portable](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/GPR-V2-Portable). Para ejecutarlos, ejecutar el siguiente comando situados en la carpeta correspondiente.

```
python main.py
```

Adicionalmente, se hizo el programa en [APP-Procesamiento](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/APP-Procesamiento) con el fin de procesar y graficar las mediciones hechas por el GPR. La aplicación se ejecuta de la misma forma que los programas anteriores.

## GPRs del laboratorio
El laboratorio de Desminado Humanitario de la Universidad de los Andes cuenta con un GPR fijo ubicado en una caja de tierras y un GPR portable diseñado para la toma de muestras en exteriores.

### Laboratorio de Desminado Humanitario

[![Alt text](https://img.youtube.com/vi/nFN6xrzAZf0/0.jpg)](https://www.youtube.com/watch?v=nFN6xrzAZf0)

### GPR Laboratorio de desminado 

[![Alt text](https://img.youtube.com/vi/YYFIdmVp42w/0.jpg)](https://www.youtube.com/watch?v=YYFIdmVp42w)

### GPR Portable

[![Alt text](https://img.youtube.com/vi/uP6CfT2qYKs/0.jpg)](https://www.youtube.com/watch?v=uP6CfT2qYKs)

## Bases de datos
En este enlace de [Google Drive](https://drive.google.com/drive/u/1/folders/1AtGNdvX9DbkHRUMq4o7JJagvuWf7gbRh) se encuentran para su descarga las mediciones tomadas en el laboratorio con el GPR. Se recomienda revisar el [manual de procesamiento GPR](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/manuales/01%20procesamiento%20de%20datos%20de%20GPR.pdf) en el capítulo 3 donde se describe la nomenclatura utilizada en los metadatos de los archivos .h5 para etiquetar las mediciones hechas.



## Equipo de trabajo

Universidad de Los Andes, Bogotá D.C, Colombia.

* Roberto Bustamante Miller - Investigador principal.
* Ángel Gutierrez - Doctor en Ciencias Sociales.
* Daniel Julián González Ramírez - MSc. Ingeniería Electrónica y de Computadores.
* Nicolás Rocha Pacheco - MSc. Ingeniería Electrónica y de Computadores.
* Luis Felipe Quiroga Fuquen - Asistente graduado Maestría de Investigación.
* Leonel Andrés Polanía Arias - Ingeniero Electrónico y de Sistemas.
* Gabriel Andrés Pérez González - Ingeniero Electrónico.
