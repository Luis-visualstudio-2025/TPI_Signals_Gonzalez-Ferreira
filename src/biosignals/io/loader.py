# src/biosignals/io/loaders.py
import numpy as np
import os
from src.biosignals.info.Info import Info
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

def _buscar_archivo_recursivo(file_name: str, search_path: str = ".") -> str:
    """Recorre las carpetas para localizar el archivo únicamente por su nombre."""
    if os.path.exists(file_name):
        return file_name
    nombre_base = os.path.basename(file_name)
    for root, dirs, files in os.walk(search_path):
        if nombre_base in files:
            ruta_encontrada = os.path.join(root, nombre_base)
            print(f"🎯 Archivo localizado en: '{ruta_encontrada}'")
            return ruta_encontrada
    raise FileNotFoundError(f"❌ Error: No se encontró el archivo '{nombre_base}'.")

def load_signal(file_path: str, signal_class: type = RawSignal, fs: float = 250.0, **kwargs) -> RawSignal:
    """
    Cargador inteligente.
    Combina formato automático de matrices con metadatos clínicos predeterminados.
    """
    # 1. Búsqueda y lectura de matriz
    file_path = _buscar_archivo_recursivo(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.npy':
        data = np.load(file_path)
    elif ext in ['.csv', '.txt']:
        # Extraemos parámetros de numpy configurando valores por defecto seguros
        delim = kwargs.get('delimiter', None)
        ucols = kwargs.get('usecols', None) # <--- Nueva línea para soportar filtrar columnas
        
        try:
            data = np.loadtxt(file_path, delimiter=delim, usecols=ucols)
        except ValueError:
            print("📝 Cabezal de texto detectado. Saltando primera línea...")
            data = np.loadtxt(file_path, delimiter=delim, skiprows=1, usecols=ucols)
    else:
        raise ValueError(f"Formato {ext} no soportado.")

    if data.ndim == 1:
        data = data.reshape(1, -1)

    # 2. Transposición Inteligente
    if data.shape[0] > data.shape[1]:
        print(f"🔄 Transponiendo automáticamente formato vertical a horizontal...")
        data = data.T 

    n_channels = data.shape[0]
    duration = data.shape[1] / fs

    if signal_class.__name__ == 'ECGSignal':
        tipo_defecto = 'ecg'
        cortes_defecto = [0.05, 150.0]  # Estándar para ECG
        notch_defecto = [50.0]
    elif signal_class.__name__ == 'EMGSignal':
        tipo_defecto = 'emg'
        cortes_defecto = [10.0, 500.0]  # Estándar para EMG
        notch_defecto = [50.0]
    else:
        tipo_defecto = 'eeg'
        cortes_defecto = [0.5, 40.0]    # Estándar para EEG
        notch_defecto = [50.0]
        
    # Si el usuario pasa los datos en los kwargs, usamos los del usuario.
    # Si no los pasa, usamos los valores por defecto calculados.
    ch_types = kwargs.get('tipos_canales', [tipo_defecto] * n_channels)
    ch_names = kwargs.get('nombre_canales', [f"{tipo_defecto.upper()}_{i+1}" for i in range(n_channels)])
    fc_corte = kwargs.get('frecuencias_corte', cortes_defecto)
    fc_notch = kwargs.get('frecuencias_notch', notch_defecto)

    # Construcción del objeto Info dinámico
    info = Info(
        nombre_canales=ch_names,
        tipos_canales=ch_types,
        bad_channels=kwargs.get('bad_channels', []),
        frecuencia_muestreo=fs,
        duracion=duration,
        info_experimento=kwargs.get('info_experimento', "Carga externa"),
        info_experimentador=kwargs.get('info_experimentador', "Usuario"),
        eventos=kwargs.get('eventos', None),
        frecuencia_linea=kwargs.get('frecuencia_linea', 50.0),
        frecuencias_corte=fc_corte,   # <--- Dinámico 
        frecuencias_notch=fc_notch    # <--- Dinámico 
    )
    # =====================================================================

    # 4. Estructura base de Eventos y Anotaciones
    eventos_obj = kwargs.get('eventos', Eventos([]))
    kwargs_anotaciones = kwargs.get('anotaciones', None)
    if isinstance(kwargs_anotaciones, Anotaciones):
        anotaciones_obj = kwargs_anotaciones
    else:
        anotaciones_obj = Anotaciones(onset=[], duration=[], description=[])

    return signal_class(
        info=info, 
        eventos=eventos_obj, 
        anotaciones=anotaciones_obj, 
        data=data,
        first_samp=kwargs.get('first_samp', 0)
    )