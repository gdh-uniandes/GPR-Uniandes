# Simulaciones

* [gprMax:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/) Contiene los archivos usados para obtener las simulaciones realizadas en gprMax. Puede encontrarse también los archivos CAD usados en la generación de los objetos hdf5 que se hizo utilizando el programa [stl-to-hdf5-gprMax](https://github.com/gaboandres1/stl-to-hdf5-gprMax). En cada subcarpeta de este directorio se encuentra un resultado de simulación que corresponde a:

    - [GSSI:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/gprMax/GSSI/) Simulación de la antena GSSI hecha a partir de la geometría del objeto en hdf5.

Además, en cada directorio de simulación, se encuentran archivos y carpetas nombrados con la siguiente estructura:

    *.in - Archivo de configuración de simulación gprMax.
    *.out - Archivo resultados de simulación gprMax.
    *.vti - Archivo de geometría de escenario gprMax.
    *.h5 - Archivo con geometría de un objeto 3D en formato hdf5.
    *_mats.txt - Archivo(s) con la distribución de materiales de un objeto 3D en formato hdf5.
    wave.txt - Archivo de texto con los valores de la forma de onda usada para la excitación de un puerto.
    Directorio stl-files: Contiene los archivos CAD usados en la generación del archivo hdf5.

* [HFSS:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/HFSS/) Contiene los archivos de simulaciones realizadas en HFSS de la antena powerLOG y resultados de simulación para escenarios específicos.

* [powerLOG_model.stl:](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/Simulaciones/powerLOG_model.stl) Modelo 3D de la antena powerLOG.
