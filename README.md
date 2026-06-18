# BioSignals - Procesamiento Digital de Señales Biomédicas

**BioSignals** es una biblioteca en Python orientada a objetos diseñada para la lectura, manipulación, procesamiento y extracción de características de señales biomédicas multicanal (EEG, ECG y EMG). 

Desarrollada como **Trabajo Práctico Integrador (TPI)** para la clase de **Programación Digital Avanzada (2026)** de la Universidad Tecnológica (UTec).

---

## Características Principales

* **Arquitectura Orientada a Objetos (OOP):** Implementación robusta utilizando herencia y polimorfismo. Una clase base `RawSignal` de la que derivan señales específicas (`EEGSignal`, `ECGSignal`, `EMGSignal`) con comportamientos propios de su dominio.
* **Validaciones Estrictas:** La clase `Info` actúa como un escudo protector, garantizando la integridad matemática y física de los metadatos (frecuencias de muestreo positivas, coherencia de canales, etc.).
* **Procesamiento Inmutable (Fail-Safe):** A través de la clase `SignalProcessor`, las señales se procesan sin mutar la data original, retornando siempre nuevas instancias procesadas.
* **Extracción de Características:** Herramientas nativas para aplicar Transformada Rápida de Fourier (FFT), Transformada de Hilbert y Espectrogramas mediante la clase `ExtraerCaracteristicas`.
* **Manejo de Épocas:** Segmentación de señales continuas en ventanas de tiempo discretas (`Epocas`) relativas a eventos específicos, facilitando el análisis ERP/ERD.
---

## ⚠️ Nota Importante sobre la Carga de Datos (Para la Evaluación)

El módulo de entrada/salida (`loader.py` y su función `load_signal`) ha sido diseñado con inteligencia paramétrica para facilitar la evaluación con archivos reales y simulados:

1. **Formatos Admitidos:** El cargador soporta archivos nativos de NumPy (`.npy`) y archivos de texto plano (`.csv`, `.txt`). Al estar diseñado con `**kwargs`, es capaz de leer delimitadores dinámicos e ignorar automáticamente metadatos en texto o marcas de tiempo mediante parámetros como `usecols` y `skiprows`.
2. **Estricto Estándar de Dimensiones (`Canales x Muestras`):** Por diseño arquitectónico, todas las clases núcleo del proyecto (`RawSignal`, `EEGSignal`, `SignalProcessor`, etc.) exigen **obligatoriamente** que la matriz de datos mantenga la dimensionalidad horizontal: `(canales x muestras)`.
3. **Transposición Automática (Auto-Fix):** Dado que muchos equipos biomédicos exportan en formato vertical `(muestras x canales)`, el loader implementa una verificación dimensional. Si detecta que la matriz ingresa de forma incorrecta, **la transpone y reorganiza automáticamente a `(canales x muestras)`** antes de inyectarla en el sistema, asegurando que el flujo de procesamiento nunca falle por incompatibilidad de dimensiones.

---
## 2. Instrucciones de instalación

Para utilizar la biblioteca **BioSignals** en tu entorno local, sigue estos pasos:

* **Paso 1: Clonar el repositorio**
Descarga el código fuente a tu computadora utilizando Git:
```bash
git clone [https://github.com/Luis-visualstudio-2025/TPI_Signals_Gonzalez-Ferreira.git](https://github.com/Luis-visualstudio-2025/TPI_Signals_Gonzalez-Ferreira.git)
cd "aqui la ruta donde quieres instalar el repositorio"

* **Paso 2: Crear un entorno virtual (Recomendado)**
Para mantener las dependencias aisladas, es una buena práctica crear un entorno virtual:

```bash
python -m venv venv

# Para activarlo en Windows:
venv\Scripts\activate
# Para activarlo en macOS/Linux:
source venv/bin/activate

* **Paso 3: Instalar la biblioteca y sus dependencias**
Este proyecto utiliza el estándar moderno `pyproject.toml`. Para instalar la librería junto con todas sus dependencias automáticamente, sitúate en la raíz del proyecto y ejecuta:

```bash
pip install -e .   

#El flag -e instala el proyecto en modo "editable", lo que significa que si haces cambios en el código fuente, se reflejarán instantáneamente sin tener que volver a instalar).
---

## 📂 Estructura del Proyecto

```text
TPI_SIGNALS_GONZALEZ-FERREIRA/
│
|── Docs-/
|   └── DiagramaUML.jpeg
├── src/
│   └── biosignals/
│       ├── epocas/             # Segmentación temporal de señales
│       │   └── Epocas.py
│       ├── eventos/            # Manejo de marcadores y anotaciones
│       │   ├── Anotaciones.py
│       │   └── Eventos.py
│       ├── info/               # Metadatos y validaciones estrictas
│       │   └── Info.py
|       |   io/
|       |   └── loader.py       # Cargar archivos .txt, .csv o .npy
│       ├── preprocesamiento/   # Filtrado, inmutabilidad y extracción
│       │   ├── Dataset.py
│       │   ├── ExtraerCaracteristicas.py
│       │   └── SignalProcessor.py
│       |── signals/            # Estructuras base y derivadas
│       |   ├── ECGSignal.py
│       |   ├── EEGsignal.py
│       |   ├── EMGSignal.py
│       |   └── RawSignal.py
|       ├── visualización
│           └── MotorGrafico.py
|
|── test/                       # Suite de pruebas unitarias (Pytest)
|   ├── demo_motor_grafico.py
|   ├── test_anotaciones.py
|   ├── test_dataset.py
|   ├── test_ecg.py
|   ├── test_eeg.py
|   ├── test_emg.py
|   ├── test_epocas.py
|   ├── test_eventos.py
|   ├── test_extraer_caracteristicas.py
|   ├── test_info.py
|   ├── test_loader.py
|   ├── test_motor_grafico.py
|   ├── test_raw_signal.py
|   └── test_signal_processor.py
|
└── pyproject.toml    
---


## 4. Forma de ejecutar los test

El proyecto cuenta con una sólida suite de pruebas unitarias implementada con `pytest`.

* **Ejecutar todos los tests:**
  Sitúate en la raíz del proyecto y ejecuta:
```bash
    pytest test/ -v

Ejecutar tests de un módulo específico:
Si deseas probar únicamente un componente (por ejemplo, RawSignal), puedes especificar el archivo:

```bash
    pytest test/test_raw_signal.py -v -s´

#El flag -s es útil para visualizar los print() durante la ejecución.
---


## 5. Ejemplo mínimo de uso
import numpy as np

# 1. IMPORTACIONES DE TU ARQUITECTURA DE BIOMEDICINA
from src.biosignals.io.loader import load_signal  # Tu último loader inteligente
from src.biosignals.signals.EEGsignal import EEGSignal
from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor
from src.biosignals.preprocesamiento.ExtraerCaracteristicas import ExtraerCaracteristicas
from src.biosignals.visualización.MotorGrafico import MotorGrafico

if __name__ == "__main__":
    print("=================================================================")
    print(" PASO 1: CARGA DE DATOS USANDO TU LOADER INTELIGENTE POLIMÓRFICO")
    print("=================================================================")
    
    # Archivo de destino (Tu loader lo buscará recursivamente si no está en la raíz)
    nombre_archivo = "eeg.txt"
    frecuencia_muestreo = 250.0  # Hz estándar para este registro

    # Mapeo clínico real del sistema 10-20 presente en las columnas de eeg.txt
    canales_clinicos = [
        'Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2', 'F7', 'F8', 
        'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz', 'Pz', 'Oz', 'FC1', 'FC2', 'CP1', 'CP2', 
        'FC5', 'FC6', 'CP5', 'CP6', 'TP9', 'TP10', 'POz', 'ECG'
    ]

    # Invocamos la función load_signal.
    # El loader realizará automáticamente:
    #  - Búsqueda recursiva del archivo en tus carpetas.
    #  - Salto de cabecera de texto (al capturar el ValueError).
    #  - Transposición automática de formato Vertical a Horizontal (Canales x Muestras).
    #  - Asignación de bandas de corte clínicas por defecto de EEG [0.5, 40.0] Hz.
    senal_eeg = load_signal(
        file_path=nombre_archivo,
        signal_class=EEGSignal,
        fs=frecuencia_muestreo,
        nombre_canales=canales_clinicos,  # Sobreescribimos los nombres genéricos por defecto
        info_experimento="Registro Clínico de Prueba S10-20",
        info_experimentador="Luis Gonzalez"
    )
    
    print(" Señal cargada y encapsulada con éxito en un objeto EEGSignal.")

    print("\n=================================================================")
    print(" PASO 2: COMPROBACIÓN DE DIMENSIONES Y CONFIGURACIÓN CLÍNICA")
    print("=================================================================")
    print(f"Dimensiones de la matriz (data): {senal_eeg.data.shape} -> ¡Organizado como (Canales x Muestras)!")
    print(f"Frecuencia de Muestreo: {senal_eeg.info.frecuencia_muestreo} Hz")
    print(f"Cantidad Total de Canales: {senal_eeg.n_channels()}")
    print(f"Cantidad de Muestras Temporales: {senal_eeg.n_samples()}")
    print(f"Duración de la Grabación: {senal_eeg.duration():.2f} segundos")
    print(f"Filtros analógicos/clínicos por defecto: {senal_eeg.info.frecuencias_corte} Hz")

    print("\n=================================================================")
    print(" PASO 3: PIPELINE DE PROCESAMIENTO DIGITAL (INMUTABLE)")
    print("=================================================================")
    # Instanciamos el procesador asignándole la señal cruda
    procesador = SignalProcessor(signal=senal_eeg)
    
    # 1. Eliminamos el offset de corriente continua (Línea base) centrando las señales en 0.
    # Nota: Tu SignalProcessor devuelve una copia modificada sin alterar 'senal_eeg'
    senal_sin_dc = procesador.remove_baseline()
    
    # 2. Aplicamos un suavizado pasabajos (media móvil de 5 muestras) a las señales centradas
    senal_filtrada = SignalProcessor(signal=senal_sin_dc).apply_lowpass(ventana=5)
    print(" Filtrado completado. Se generó un nuevo objeto manteniendo la señal original intacta.")

    print("\n=================================================================")
    print(" PASO 4: EXTRACCIÓN DE MÉTRICAS Y CARACTERÍSTICAS BIOMÉDICAS")
    print("=================================================================")
    # Instanciamos el extractor utilizando la señal previamente filtrada
    extractor = ExtraerCaracteristicas(signal=senal_filtrada)
    
    # Calculamos métricas universales sobre el eje del tiempo
    lista_medias = extractor.mean()
    lista_desviaciones = extractor.std()
    
    # Desplegamos resultados de canales de relevancia clínica frontal, occipital y cardíaca
    canales_interes = ['Fp1', 'O1', 'ECG']
    for ch in canales_interes:
        idx = canales_clinicos.index(ch)
        print(f"Canal [{ch}] -> Media: {lista_medias[idx]:.4f} µV | Desviación Estándar (uV): {lista_desviaciones[idx]:.4f}")

    print("\n=================================================================")
    print("PASO 5: VISUALIZACIÓN EN RENGLONES INDEPENDIENTES (SUBPLOTS)")
    print("=================================================================")
    # Seleccionamos un subconjunto claro de canales para desplegar en pantalla
    canales_a_graficar = ['Fp1', 'Fp2', 'O1', 'O2', 'ECG']
    
    # Configuramos el motor gráfico interactivo
    motor = MotorGrafico(
        senal_actual=senal_filtrada,
        epocas=None,
        modo_visualizacion="señal",
        canales_visibles=canales_a_graficar,
        mostrar_anotaciones=False,
        rango_tiempo=(0.0, 40.0)  # Graficamos una ventana de tiempo de los primeros 40 segundos
    )
    
    print(f"Renderizando subgráficas para los canales: {canales_a_graficar}...")
    # Llamamos al nuevo método multi-renglón que integraste en tu clase MotorGrafico
    motor.graficar_por_renglones(mostrar=True)
    
    print("=================================================================")
    print(" Fin de la ejecución del pipeline completo de BioSignals.")
    print("=================================================================")
---
