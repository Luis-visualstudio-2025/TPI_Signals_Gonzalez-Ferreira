import numpy as np


from src.biosignals.io.loader import load_signal  
from src.biosignals.signals.EEGsignal import EEGSignal
from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor
from src.biosignals.preprocesamiento.ExtraerCaracteristicas import ExtraerCaracteristicas
from src.biosignals.visualización.MotorGrafico import MotorGrafico

if __name__ == "__main__":
    print("=================================================================")
    print(" CARGA DE DATOS USANDO EL LOADER")
    print("=================================================================")
    
    # Archivo de destino (El loader lo buscará recursivamente si no está en la raíz)
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
    print(" COMPROBACIÓN DE DIMENSIONES Y CONFIGURACIÓN CLÍNICA")
    print("=================================================================")
    print(f"Dimensiones de la matriz (data): {senal_eeg.data.shape} -> ¡Organizado como (Canales x Muestras)!")
    print(f"Frecuencia de Muestreo: {senal_eeg.info.frecuencia_muestreo} Hz")
    print(f"Cantidad Total de Canales: {senal_eeg.n_channels()}")
    print(f"Cantidad de Muestras Temporales: {senal_eeg.n_samples()}")
    print(f"Duración de la Grabación: {senal_eeg.duration():.2f} segundos")
    print(f"Filtros analógicos/clínicos por defecto: {senal_eeg.info.frecuencias_corte} Hz")

    print("\n=================================================================")
    print(" PROCESAMIENTO DIGITAL (INMUTABLE)")
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
    print(" EXTRACCIÓN DE MÉTRICAS Y CARACTERÍSTICAS BIOMÉDICAS")
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
    print("VISUALIZACIÓN EN RENGLONES (SUBPLOTS)")
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
    print(" Fin de la ejecución .")
    print("=================================================================")
