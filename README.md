# GPR-Uniandes

Proyecto Desminado Humanitario para la detección de minas terrestres con el uso de un GPR.
En este repositorio contiene los siguientes archivos del proyecto.
* Software para el control de los GPR del laboratorio Desminado Humanitario.
* Software para el procesamiento de las mediciones hechas con el GPR del laboratorio.
* Manuales y documentación del software de los equipos GPR.
* Informes de mediciones de GPR y técnicas de procesamiento aplicadas (así como enlace de descarga a los datos tomados).
* Archivos de simulaciones en HFSS y gprMax, junto con su respectivos informes.
* Contenido multimedia (fotos y videos) para observar los equipos de laboratorio.
* Links de acceso a repositorios complementarios del proyecto.

Para conocer rápidamente cómo poner en marcha el GPR, tomar muestras y graficarlas se recomienda revisar el [manual de primer uso del GPR](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Manual_Primer_Uso.pdf). Se recomienda también revisar cada sección de este README para ubicar todos los elementos presentes en este repositorio.

## Instalación

Para utilizar todo software de este repositorio es necesario tener instalado Python 3. Además, instalar las dependencias de Python necesarias ejecutando el siguiente comando.

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

## Documentación
En el directorio [Documentos](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/Documentos) se encuentran los manuales, informes y documentos realizados en el proyecto. La lista de documentos del proyecto es la siguiente.


### Manuales
* [Guide of GPR-20 data: specification, formatting, preprocessing and processing](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/01%20procesamiento%20de%20datos%20de%20GPR.pdf)

* [Manual de uso para la aplicación de procesamiento de datos de GPR](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Manual_APP_Procesamiento.pdf)

* [Manual de primer uso del GPR del proyecto Desminado Humanitario](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Manual_Primer_Uso.pdf)

* [Manual de programador para el GPR de laboratorio](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Manual_Programador_GPR.pdf)

* [Manual de usuario para el GPR de laboratorio](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Manual_Usuario_GPR.pdf)

### Informes y reportes

* [Mediciones Machine Learning](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Mediciones_Machine_Learning.pdf)

* [Sistema de detección de minas GPR y Machine Learning](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Sistema_de_detecci_n_de_minas_GPR_y_Machine_Learning.pdf) 

* [UDT Migration](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/UDT_Migration.pdf)

* [Simulaciones GPR en HFSS](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Simulaciones_GPR_HFSS.pdf)

* [Conversion de archivos CAD gprMax](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Conversion_de_archivos_CAD_gprMax.pdf)

* [Algoritmo MPDL-LR para la detección y clasificación de Minas](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Detecci%C3%B3n%20y%20Clasificaci%C3%B3n%20de%20Minas%20usando%20el%20algoritmo%20MPDL_LR.pdf)

* [Estimación de la permitividad y espesor de capas](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Estimaci%C3%B3n%20de%20la%20permitividad%20y%20espesor%20de%20un%20medio%20por%20capas.pdf)

* [Desminado Humanitario en Colombia visto como Sistema](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Desminado%20Humanitario%20en%20Colombia%20visto%20como%20Sistema.pdf)

## Archivos de simulación
En la carpeta [Simulaciones](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/Simulaciones) se han puesto todos los archivos necesarios para simular en HFSS y/o gprMax y llegar a los resultados obtenidos en los escenarios propuestos. Revisar el [README](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/Simulaciones/README.md) en la carpeta para entender la distribución de los archivos. También, en los informes de simulación en [HFSS](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Simulaciones_GPR_HFSS.pdf) y [gprMax](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Conversion_de_archivos_CAD_gprMax.pdf) se encuentran hipervinculos a la carpeta que contiene los archivos de soporte de las simulaciones en cuestión, por lo que se recomienda su lectura.

## GPRs del laboratorio
El laboratorio de Desminado Humanitario de la Universidad de los Andes cuenta con un GPR fijo ubicado en una caja de tierras y un GPR portable diseñado para la toma de muestras en exteriores.

### Laboratorio de Desminado Humanitario

[![Alt text](https://img.youtube.com/vi/nFN6xrzAZf0/0.jpg)](https://www.youtube.com/watch?v=nFN6xrzAZf0)

### GPR Laboratorio de desminado 

[![Alt text](https://img.youtube.com/vi/YYFIdmVp42w/0.jpg)](https://www.youtube.com/watch?v=YYFIdmVp42w)

### GPR Portable

![Image](Contenido%20multimedia/GPR%20Portable%20V2/GPR%20Portable%20V2%20-%203.jpg)

## Bases de datos
En este enlace de [Google Drive](https://drive.google.com/drive/u/1/folders/1AtGNdvX9DbkHRUMq4o7JJagvuWf7gbRh) se encuentran para su descarga las mediciones tomadas en el laboratorio con el GPR. Se recomienda revisar el [manual de procesamiento GPR](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/01%20procesamiento%20de%20datos%20de%20GPR.pdf) en el capítulo 3 donde se describe la nomenclatura utilizada en los metadatos de los archivos .h5 para etiquetar las mediciones hechas.

## Repositorios adicionales del proyecto Desminado Humanitario
Otros archivos y documentos del proyecto Desminado Humanitario que no están presentes en este repositorio, se encuentran en los siguientes enlaces.

* [GPR-20 Start Guide](https://github.com/gdh-uniandes/gpr20_start_guide) - Documento con la guía de inicio del GPR-20, el cual es un GPR portable con extensa documentación, pensado para que pueda construirse por cualquier persona con una impresora 3D. En este documento se encuentra la descripción del GPR-20 y enlaces para acceder a sus manuales y archivos de soporte.

* [stl-to-hdf5-gprMax](https://github.com/gaboandres1/stl-to-hdf5-gprMax) - Repositorio para instalar la herramienta para convertir archivos CAD en geometrías gprMax. En este repositorio está explicado el uso del software y su instalación.

## Grupo de Desminado Humanitario

Universidad de Los Andes, Bogotá D.C, Colombia.

* Roberto Bustamante Miller - Investigador principal.
* Ángel Gutierrez - Doctor en Ciencias Sociales.
* Daniel Julián González Ramírez - MSc. Ingeniería Electrónica y de Computadores.
* Nicolás Rocha Pacheco - MSc. Ingeniería Electrónica y de Computadores.
* Luis Felipe Quiroga Fuquen - Asistente graduado Maestría de Investigación.
* Leonel Andrés Polanía Arias - Ingeniero Electrónico y de Sistemas.
* Gabriel Andrés Pérez González - Ingeniero Electrónico.
* Juan Pablo Reyes Fajardo - Ingeniero Mecánico

Contacto: desminadohumanitario@uniandes.edu.co
