# scripts procesamiento

Los scripts de Python presentes en esta carpeta ejecutan el procesamiento de datos para una toma de datos almacenada en una ruta determinada. La teoría al respecto de los métodos numéricos que se ejecutan en estos scripts está documentada [aquí](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/manuales/01%20procesamiento%20de%20datos%20de%20GPR.pdf). A continuación se describe el proceso que se debe seguir para procesar las mediciones y obtener una mapeo 3D de las mediciones en el dominio del tiempo. 

* 1. [ifft_multiple_files.py](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/scripts%20procesamiento/01_ifft_gpr/ifft_multiple_files.py): Ejecuta la transformada inversa de Fourier para las mediciones en el dominio de la frecuencia y las almacena en la carpeta "Time". La carpeta resultante se crea en la ruta indicada en la variable 'directory'; en esta misma ruta debe encontrarse la carpeta "Freq" con las mediciones en frecuencia.

* 2. [merge_ascans.py](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/scripts%20procesamiento/02_gpr_utilities/merge_ascans.py): Obtiene el vector de tiempos y un archivo .h5 con las mediciones comprimidas e información al respecto.

* 3. [c_scan_background_removal.py](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/scripts%20procesamiento/03_processing/c_scan_background_removal.py): Obtiene el promedio de las mediciones para removerlo de estas.
* 4. [c_scan_background_subtraction.py](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/scripts%20procesamiento/03_processing/c_scan_background_subtraction.py): Resta dos conjuntos de mediciones. Esto es útil para remover el ruido de las muestras.

* 5. [parallel_kirchhoff_migration.py](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/scripts%20procesamiento/03_processing/parallel_kirchhoff_migration.py): Ejecuta el algoritmo de migración descrito en el [manual](https://github.com/gdh-uniandes/GPR-Uniandes/blob/main/manuales/01%20procesamiento%20de%20datos%20de%20GPR.pdf).

* [04_plotting](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/scripts%20procesamiento/04_plotting): En esta carpeta se encuentran diferentes scripts para obtener plots de las mediciones migradas, C-Scan y B-Scan.

## Códigos fuente para la detección de objetos

Los notebooks presentes en [05_detection](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/scripts%20procesamiento/05_detection) corresponden al código fuente empleado en la detección de objetos que se implementó en los documentos [Mediciones Machine Learning](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/Documentos/Mediciones_Machine_Learning.pdf), [Sistema de detección de minas GPR y Machine Learning](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/Documentos/Sistema_de_detecci_n_de_minas_GPR_y_Machine_Learning.pdf) y [UDT Migration](https://github.com/gdh-uniandes/GPR-Uniandes/tree/main/Documentos/UDT_Migration.pdf).

