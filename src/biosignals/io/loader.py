# src/biosignals/io/loaders.py
import numpy as np
import os
from src.biosignals.info.Info import Info
from src.biosignals.signals.RawSignal import RawSignal

def load_signal(file_path: str, signal_class: type = RawSignal, fs: float = 250.0, **kwargs) -> RawSignal:
    """
    Cargador centralizado. 
    1. Abre el archivo.
    2. Crea el objeto Info necesario para la clase de señal.
    3. Retorna la señal instanciada.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    # Carga de datos (agnóstica del formato)
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.npy':
        data = np.load(file_path)
    elif ext in ['.csv', '.txt']:
        data = np.loadtxt(file_path, delimiter=kwargs.get('delimiter', ','))
    else:
        raise ValueError(f"Formato {ext} no soportado.")

    if data.ndim == 1:
        data = data.reshape(1, -1)

    # Construcción del objeto Info 
    n_channels = data.shape[0]
    duration = data.shape[1] / fs

    # 1. Determinamos valores lógicos por defecto según el tipo de clase de señal
    if signal_class.__name__ == 'ECGSignal':
        tipo_defecto = 'ecg'
        cortes_defecto = [0.05, 150.0]  # Estándar para ECG
        notch_defecto = [50.0]
    elif signal_class.__name__ == 'EMGSignal':
        tipo_defecto = 'emg'
        cortes_defecto = [10.0, 500.0]  # Estándar para EMG
        notch_defecto = [50.0]
    else:
        tipo_defecto = 'EEGSignal'
        cortes_defecto = [0.5, 40.0]    # Estándar para EEG
        notch_defecto = [50.0]
        
    # 2. Si el usuario pasa los datos en los kwargs, usamos los del usuario.
    # Si no los pasa, usamos los valores por defecto que acabamos de calcular.
    ch_types = kwargs.get('tipos_canales', [tipo_defecto] * n_channels)
    ch_names = kwargs.get('nombre_canales', [f"CH_{i+1}" for i in range(n_channels)])
    fc_corte = kwargs.get('frecuencias_corte', cortes_defecto)
    fc_notch = kwargs.get('frecuencias_notch', notch_defecto)

    # 3. Construcción del objeto Info dinámico
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
    

    # Retorno de la señal ya instanciada con su Info validada
    # Asumimos que eventos y anotaciones se inicializan vacíos por defecto
    from src.biosignals.eventos.Eventos import Eventos
    from src.biosignals.eventos.Anotaciones import Anotaciones
    
    # 2. Procesamiento dinámico de EVENTOS
    kwargs_eventos = kwargs.get('eventos', None)
    if kwargs_eventos is None:
        # Si no pasaron nada, creamos un objeto Eventos vacío de forma segura
        eventos_obj = Eventos([])
    elif isinstance(kwargs_eventos, Eventos):
        # Si el usuario ya se tomó el trabajo de pasar el objeto Eventos armado, lo usamos directamente
        eventos_obj = kwargs_eventos
    elif isinstance(kwargs_eventos, list):
        # Si el usuario pasó una lista cruda de tuplas [(muestra, id), ...], 
        # fabricamos automáticamente el objeto Eventos por él
        eventos_obj = Eventos(eventos=kwargs_eventos, mapeo=kwargs.get('mapeo_eventos', None))
    else:
        raise TypeError("El parámetro 'eventos' debe ser una lista de tuplas o un objeto Eventos.")

    # 3. Procesamiento dinámico de ANOTACIONES
    kwargs_anotaciones = kwargs.get('anotaciones', None)
    if kwargs_anotaciones is None:
        # Si no pasaron nada, creamos un objeto Anotaciones vacío por defecto
        anotaciones_obj = Anotaciones(onset=[], duration=[], description=[])
    elif isinstance(kwargs_anotaciones, Anotaciones):
        # Si ya es un objeto Anotaciones estructurado, lo reutilizamos
        anotaciones_obj = kwargs_anotaciones
    elif isinstance(kwargs_anotaciones, dict):
        # Si pasaron un diccionario con las listas sueltas, por ejemplo:
        # {'onset': [1.0], 'duration': [0.5], 'description': ['Parpadeo']}
        # Construimos el objeto dinámicamente despaquetando sus claves
        anotaciones_obj = Anotaciones(
            onset=kwargs_anotaciones.get('onset', []),
            duration=kwargs_anotaciones.get('duration', []),
            description=kwargs_anotaciones.get('description', []),
            t0=kwargs_anotaciones.get('t0', None),
            ch_names=kwargs_anotaciones.get('ch_names', None)
        )
    else:
        raise TypeError("El parámetro 'anotaciones' debe ser un dict con listas o un objeto Anotaciones.")

    # 4. Retornamos la señal instanciada con todos sus objetos satélite bien construídos
    return signal_class(
        info=info, 
        eventos=eventos_obj, 
        anotaciones=anotaciones_obj, 
        data=data, 
        first_samp=kwargs.get('first_samp', 0)          # Si el usuario no especifica el primer sample, asumimos que es 0 por defecto
    )

