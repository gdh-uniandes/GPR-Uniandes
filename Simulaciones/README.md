# Simulaciones

* [gprMax:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/) Contiene los archivos usados para obtener las simulaciones realizadas en gprMax, cuyos resultados son mostrados en este [informe](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Conversion_de_archivos_CAD_gprMax.pdf). Puede encontrarse también los archivos CAD usados en la generación de los objetos hdf5 que se hizo utilizando el programa [stl-to-hdf5-gprMax](https://github.com/gaboandres1/stl-to-hdf5-gprMax). En cada subcarpeta de este directorio se encuentra un resultado de simulación que corresponde a:
    * [GSSI:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/GSSI/) Simulación de la antena GSSI hecha a partir de la geometría del objeto en hdf5.
    * [MALA:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/MALA/) Simulación de la antena MALA hecha a partir de la geometría del objeto en hdf5.
    * [Coaxial:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/MALA/) Simulación de una linea de transmisión coaxial.
    * [Horn:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/MALA/) Simulación de la antena de bocina hecha a partir de la geometría del objeto en hdf5.
    * [PowerLOG:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/PowerLOG/) Simulaciones de la antena PowerLOG hecha a partir de la geometría del objeto en hdf5.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Además, en cada directorio de simulación, se encuentran archivos y carpetas nombrados con la siguiente estructura:

    *.in - Archivo(s) de configuración de simulación gprMax.
    *.out - Archivo(s) resultados de simulación gprMax.
    *.vti - Archivo(s) de geometría de escenario gprMax.
    *.h5 - Archivo con geometría de un objeto 3D en formato hdf5.
    *_mats.txt - Archivo(s) con la distribución de materiales de un objeto 3D en formato hdf5.
    wave.txt - Archivo de texto con los valores de la forma de onda usada para la excitación de un puerto.
    Directorio stl-files: Contiene los archivos CAD usados en la generación del archivo hdf5.

* [HFSS:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/HFSS/) Contiene los archivos de simulaciones realizadas en HFSS de la antena powerLOG y resultados de simulación para escenarios específicos. El informe de las simulaciones de esta carpeta se encuentra [aquí](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Documentos/Simulaciones_GPR_HFSS.pdf)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Para cada escenario de simulación, se encuentran archivos nombrados con la siguiente estructura:

    *.mstat - Estadísticas de mallado del escenario en HFSS.
    *.prof - Perfil de uso de recursos computacionales para la ejecución del escenario en HFSS.
    *.s1p o .s2p - Parámetros S para los puertos que componen el escenario, indicadas para las frecuencias que este se simula.
    *.png - Imagen que muestra el proceso de convergencia del escenario al ser ejecutado.
    *-animation_1GHz_XY.gif - Archivo con animación de magnitud de campos electromagnéticos sobre un plano del escenario. En este caso, se presenta la animación de magnitud del campo eléctrico sobre el plano XY para una frecuencia de 1GHz.
