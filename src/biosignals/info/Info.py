from typing import List, Dict, Any, Optional, Union

class Info:                                                         # Definimos la clase Info para almacenar información relevante de las señales
    def __init__(
        self, 
        nombre_canales: List[str],                                  # Lista de nombres de canales (str) que describe cada canal de la señal.
        tipos_canales: List[str],                                   # Lista de tipos de canales (str) que describe el tipo de cada canal (ej: EEG, ECG, EMG, etc.).
        bad_channels: List[str],                                    # Lista de canales marcados como "malos" o no confiables. Puede contener nombres de canales o índices.
        frecuencia_muestreo: float,                                 # Frecuencia de muestreo de la señal en Hz (float). Debe ser estrictamente mayor a 0.
        duracion: float,                                            # Duración de la señal en segundos (float). Debe ser mayor o igual a 0.
        info_experimento: str = "",                                 # Información adicional sobre el experimento o contexto de la señal (str). Puede ser una descripción, notas, etc.
        info_experimentador: str = "",                              # Información sobre el experimentador o persona que realizó la adquisición de la señal (str). Puede incluir nombre, institución, etc.
        eventos: Any = None,                                        # Información sobre eventos asociados a la señal. Puede ser de cualquier tipo (Any) y puede incluir marcas de tiempo, anotaciones, etc.
        frecuencia_linea: float = 50.0, 
        frecuencias_corte: Optional[List[float]] = None,            # Lista de frecuencias de corte para filtros aplicados a la señal. Debe ser una lista de dos elementos [frecuencia_baja, frecuencia_alta]. Si no se proporciona, se establece como [0.0, 0.0].
        frecuencias_notch: Optional[List[float]] = None             # Lista de frecuencias para filtros notch aplicados a la señal. Puede ser una lista de frecuencias específicas. Si no se proporciona, se establece como una lista vacía.
    ):        
        # --- NUEVA VALIDACIÓN DE TIPOS INTERNOS ---
        if not all(isinstance(ch, str) for ch in nombre_canales):
            raise TypeError("Todos los nombres de canales deben ser cadenas de texto (str).")

        if not all(isinstance(ch, str) for ch in tipos_canales):
            raise TypeError("Todos los tipos de canales deben ser cadenas de texto (str).")

        if not all(isinstance(ch, str) for ch in bad_channels):
            raise TypeError("Todos los canales marcados como 'malos' deben ser cadenas de texto (str).")

        # Ahora que sabemos que son todos strings, los asignamos de forma segura:
        self.nombre_canales = nombre_canales                        
        self.tipos_canales = tipos_canales                          
        
        # --- validación de cruzada de atributos ---
        # Validamos que la cantidad de nombres de canales coincida con la cantidad de tipos de canales
        if len(self.nombre_canales) != len(self.tipos_canales):
            raise ValueError("La cantidad de nombres de canales debe coincidir con la cantidad de tipos de canales.")
            
        self.bad_channels = bad_channels                            
        # Usamos los setters definidos abajo para validar datos críticos
        self.frecuencia_muestreo = frecuencia_muestreo              
        self.duracion = duracion                                    
        
        self.info_experimento = info_experimento                    
        self.info_experimentador = info_experimentador              
        self.eventos = eventos                                      
        self.frecuencia_linea = frecuencia_linea                    
        
        # Validamos que los filtros tengan valores coherentes por defecto
        self.frecuencias_corte = frecuencias_corte if frecuencias_corte is not None else [0.0, 0.0]
        self.frecuencias_notch = frecuencias_notch if frecuencias_notch is not None else []

    # Encapsulamiento (Properties y Setters)

    @property
    def frecuencia_muestreo(self) -> float:
        return self._frecuencia_muestreo

    @frecuencia_muestreo.setter
    def frecuencia_muestreo(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("La frecuencia de muestreo debe ser un número.")
        if value <= 0:
            raise ValueError("La frecuencia de muestreo debe ser estrictamente mayor a 0 Hz.")
        self._frecuencia_muestreo = float(value)

    @property
    def duracion(self) -> float:
        return self._duracion

    @duracion.setter
    def duracion(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("La duración debe ser un número.")
        if value < 0:
            raise ValueError("La duración no puede ser negativa.")
        self._duracion = float(value)

    @property
    def frecuencias_corte(self) -> List[float]:
        return self._frecuencias_corte

    @frecuencias_corte.setter
    def frecuencias_corte(self, value: List[float]) -> None:
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError("frecuencias_corte debe ser una lista de 2 elementos: [baja, alta].")
        if value[0] >= value[1] and value[1] != 0.0:
            raise ValueError("La frecuencia de corte inferior debe ser menor a la superior.")
        self._frecuencias_corte = [float(x) for x in value]

    @property
    def n_channels(self) -> int:                                    # El TP exige que sea una propiedad. Retorna el número de canales.
        return len(self.nombre_canales)

    @property
    def n_samples(self) -> int:                                     # El TP exige que sea una propiedad. Retorna muestras totales calculadas.
        return int(round(self.frecuencia_muestreo * self.duracion))

    def __contains__(self, item: Any) -> bool:                      # Método para verificar si un item está presente en el nombre de canales
        return item in self.nombre_canales

    def __getitem__(self, key: str) -> Any:                         # Método para acceder como un diccionario (ej: info['ch_names'])
        # Buscamos la propiedad o atributo ignorando si es privado
        if hasattr(self, key):
            return getattr(self, key)
        elif hasattr(self, f"_{key}"):
            return getattr(self, f"_{key}")
        raise KeyError(f"La clave '{key}' no se encuentra en Info.")

    def __len__(self) -> int:                                       # Método para obtener la cantidad de canales (usando len(info))
        return self.n_channels

    def __str__(self) -> str:                                       # Representación textual para print(info)
        return f"Info de la señal: {self.n_channels} canales, Fs: {self.frecuencia_muestreo} Hz, duración: {self.duracion} segundos"
    
    def _to_dict(self) -> Dict[str, Any]:                           # Helper oculto para empaquetar los datos limpios
        return {
            'nombre_canales': self.nombre_canales,
            'tipos_canales': self.tipos_canales,
            'bad_channels': self.bad_channels,
            'frecuencia_muestreo': self.frecuencia_muestreo,
            'duracion': self.duracion,
            'info_experimento': self.info_experimento,
            'info_experimentador': self.info_experimentador,
            'frecuencias_corte': self.frecuencias_corte,
            'frecuencias_notch': self.frecuencias_notch
        }

    def get(self, key: str, default: Any = None) -> Any:            # Obtiene valor de forma segura
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def keys(self):                                                 # Retorna las claves de forma limpia
        return self._to_dict().keys()

    def items(self):                                                # Retorna pares clave-valor de forma limpia
        return self._to_dict().items()

    def rename_channels(self, mapping: Dict[Any, Any]) -> None:     # Método para renombrar canales a partir de un DICCIONARIO
        """
        Renombra canales de forma segura. 
        Recibe un diccionario: {'ViejoNombre': 'NuevoNombre'}
        """
        if not isinstance(mapping, dict):
            raise TypeError("Se debe proporcionar un diccionario para renombrar. Ej: {'Oz': 'O1'}")
            
        for old_name, new_name in mapping.items():
            if old_name not in self.nombre_canales:
                # El TP exige lanzar ValueError si el canal viejo no existe
                raise ValueError(f"El canal '{old_name}' no está en la lista de canales.")
            
            idx = self.nombre_canales.index(old_name)
            self.nombre_canales[idx] = new_name
            
    def frec_muestreo(self) -> float:                               # Método para obtener la frecuencia de muestreo, retorna el valor de la frecuencia de muestreo presente en la señal. En este contexto, se muestra la frecuencia de muestreo que se ha establecido para la señal.
         return self.frecuencia_muestreo