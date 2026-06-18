#  BioSignals - Procesamiento Digital de Señales Biomédicas

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

##  Estructura del Proyecto

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
El siguiente ejemplo muestra cómo cargar una señal desde un archivo (usando un Loader), instanciar una señal de tipo EEGSignal y aplicar un filtro de manera segura (inmutable):

```bash
    from src.biosignals.preprocesamiento.Loader import Loader
    from src.biosignals.signals.EEGsignal import EEGSignal
    from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor

    # 1. Cargar la señal desde un archivo (ej: .edf, .csv, o formato propio)
    # El loader retorna los componentes necesarios para la instancia
    datos_cargados = Loader.load("ruta/a/tu/archivo_eeg.edf")

    # 2. Instanciar la señal específica (EEGSignal)
    # La clase hereda de RawSignal y valida la integridad de los datos
    eeg = EEGSignal(
        info=datos_cargados.info,
        eventos=datos_cargados.eventos,
        anotaciones=datos_cargados.anotaciones,
        data=datos_cargados.data,
        first_samp=datos_cargados.first_samp
    )

    # 3. Procesamiento seguro (Inmutable)
    # SignalProcessor retorna una NUEVA instancia sin modificar 'eeg'
    procesador = SignalProcessor(eeg)
    eeg_filtrado = procesador.apply_lowpass(ventana=5)

    # 4. Análisis y Visualización
    # EEGSignal tiene métodos específicos para graficar FFT, Hilbert o Espectrogramas
    eeg_filtrado.plot_fft()
---
