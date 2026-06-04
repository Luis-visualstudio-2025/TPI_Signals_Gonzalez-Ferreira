#Clase Épocas

# Clase Épocas

import numpy as np
from typing import Union, List, Dict, Optional      # Importaciones de tipos para validación y anotaciones

from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.eventos.Eventos import Eventos


class Epocas:
    """
    Representa un conjunto de épocas obtenidas a partir de una señal biomédica y eventos.
    Cada época corresponde a un intervalo temporal alrededor de un evento.
    Forma de datos: (epocas x canales x muestras)
    """

    def __init__(
        self, 
        signal: RawSignal, 
        eventos: Union[Eventos, np.ndarray, None], 
        id_eventos: Union[int, List[int], Dict, str, List[str], None] = None, 
        tmin: float = -0.2, 
        tmax: float = 0.5, 
        picks: Union[str, List[str], None] = None,
        reject: Optional[Dict[str, float]] = None,
        _precomputed_data: Optional[np.ndarray] = None
    ):
        # Validación defensiva de tipos obligatorios
        if not isinstance(signal, RawSignal):
            raise TypeError("El parámetro 'signal' debe ser una instancia o heredar de RawSignal.")
        
        self.signal = signal
        self.eventos = eventos
        
        # Normalización interna de los identificadores de eventos
        if id_eventos is None:
            self.id_eventos = None
        elif isinstance(id_eventos, list):
            self.id_eventos = id_eventos
        else:
            self.id_eventos = [id_eventos]

        # Inicialización de propiedades mediante setters de validación
        self.tmin = tmin
        self.tmax = tmax
        
        # Normalización de canales seleccionados (picks)
        self.picks = [picks] if isinstance(picks, str) else picks
        self.reject = reject

        # Procesamiento o asignación directa de los bloques de datos
        if _precomputed_data is not None:
            self.data = _precomputed_data
        else:
            self._eventos_raw = self._normalizar_eventos(eventos)
            self.data = self._crear_epocas()

    # --- Propiedades y Validaciones (Encapsulamiento) ---

    @property
    def tmin(self) -> float:
        return self._tmin

    @tmin.setter
    def tmin(self, value: float):
        if hasattr(self, '_tmax') and value >= self._tmax:
            raise ValueError("El tiempo mínimo 'tmin' debe ser estrictamente menor que 'tmax'.")
        self._tmin = float(value)

    @property
    def tmax(self) -> float:
        return self._tmax

    @tmax.setter
    def tmax(self, value: float):
        if hasattr(self, '_tmin') and value <= self._tmin:
            raise ValueError("El tiempo máximo 'tmax' debe ser estrictamente mayor que 'tmin'.")
        self._tmax = float(value)

    # --- Métodos Privados de Procesamiento ---

    def _normalizar_eventos(self, eventos: Union[Eventos, np.ndarray, None]) -> np.ndarray:
        """Convierte las diferentes variantes de eventos de entrada a una matriz ndarray unificada."""
        if eventos is None:
            return np.array([])
        if isinstance(eventos, Eventos):
            return np.array(eventos.eventos)
        if isinstance(eventos, np.ndarray):
            if eventos.ndim != 2 or eventos.shape[1] != 2:
                raise ValueError("El ndarray de eventos debe tener dimensiones (n_eventos, 2).")
            return eventos
        raise TypeError("El formato del parámetro 'eventos' no es válido.")

    def _verificar_rechazo(self, epoca: np.ndarray) -> bool:
        """Verifica si algún canal dentro de la época supera el umbral pico a pico definido."""
        if not self.reject:
            return False
        
        # Identificamos los canales evaluados en esta época
        canales_evaluados = self.picks if self.picks else self.signal.info.nombres_canales
        
        for idx, ch_name in enumerate(canales_evaluados):
            ch_name_lower = ch_name.lower()
            pico_a_pico = np.ptp(epoca[idx]) # Calcula el rango Máximo - Mínimo (Peak-to-Peak)
            
            for criterio, umbral in self.reject.items():
                if criterio.lower() in ch_name_lower and pico_a_pico > umbral:
                    return True # La época debe ser rechazada
        return False

    def _crear_epocas(self) -> np.ndarray:
        """Segmenta la señal continua basándose en la posición temporal de los eventos válidos."""
        if self._eventos_raw.size == 0:
            return np.array([])

        fs = self.signal.info.frecuencia_muestreo
        inicio_offset = int(self.tmin * fs)
        fin_offset = int(self.tmax * fs)
        
        epocas_filtradas = []
        
        for muestra, id_evento in self._eventos_raw:
            # Filtrado por identificador de evento
            if self.id_eventos is not None and id_evento not in self.id_eventos:
                continue

            inicio_epoca = int(muestra + inicio_offset)
            fin_epoca = int(muestra + fin_offset)

            # Control estricto de desbordamiento de límites de la señal
            if inicio_epoca < 0 or fin_epoca > self.signal.n_samples():
                continue

            # Extracción del segmento temporal multicatenario
            epoca = self.signal.data[:, inicio_epoca:fin_epoca]

            # Indexación selectiva por picks si aplica
            if self.picks is not None:
                try:
                    indices = [self.signal.info.nombres_canales.index(ch) for ch in self.picks]
                    epoca = epoca[indices]
                except ValueError as e:
                    raise ValueError(f"Uno de los canales especificados en 'picks' no existe: {e}")

            # Filtrado por umbral pico a pico
            if self._verificar_rechazo(epoca):
                continue

            epocas_filtradas.append(epoca)

        return np.array(epocas_filtradas)

    # --- Métodos Públicos Requeridos ---

    def get_data(self) -> np.ndarray:
        """Devuelve la matriz tridimensional que compone todas las épocas."""
        return self.data

    def promedio(self) -> 'Epocas':
        """Calcula el promedio de las épocas y retorna una nueva instancia conservando metadatos."""
        if self.data.size == 0:
            raise ValueError("No existen épocas procesadas para calcular el promedio.")
        
        # Mantenemos las 3 dimensiones (1, canales, muestras) para preservar consistencia estructural
        data_promedio = np.mean(self.data, axis=0)[np.newaxis, :, :]
        
        return Epocas(
            signal=self.signal,
            eventos=self.eventos,
            id_eventos=self.id_eventos,
            tmin=self.tmin,
            tmax=self.tmax,
            picks=self.picks,
            reject=self.reject,
            _precomputed_data=data_promedio
        )

    def recortar(self, tmin_nuevo: float, tmax_nuevo: float) -> 'Epocas':
        """Recorta un sub-intervalo temporal interno de las épocas y retorna una nueva instancia."""
        if tmin_nuevo < self.tmin or tmax_nuevo > self.tmax:
            raise ValueError("El nuevo intervalo temporal debe estar contenido dentro del rango original.")
            
        fs = self.signal.info.frecuencia_muestreo
        idx_inicio = int((tmin_nuevo - self.tmin) * fs)
        idx_fin = int((tmax_nuevo - self.tmin) * fs)
        
        data_recortada = self.data[:, :, idx_inicio:idx_fin]

        return Epocas(
            signal=self.signal,
            eventos=self.eventos,
            id_eventos=self.id_eventos,
            tmin=tmin_nuevo,
            tmax=tmax_nuevo,
            picks=self.picks,
            reject=self.reject,
            _precomputed_data=data_recortada
        )

    def eliminar_canales(self, canales: List[str]):
        """Elimina de forma permanente una lista de canales de la estructura de datos."""
        if self.data.size == 0:
            return
            
        try:
            canales_actuales = self.picks if self.picks else self.signal.info.nombres_canales
            indices_eliminar = [canales_actuales.index(ch) for ch in canales]
        except ValueError as e:
            raise ValueError(f"Imposible eliminar canales no existentes en el conjunto: {e}")
            
        indices_mantener = [i for i in range(self.data.shape[1]) if i not in indices_eliminar]
        self.data = self.data[:, indices_mantener, :]
        
        # Sincronizamos la lista de canales vigentes si existía una selección previa
        if self.picks:
            self.picks = [ch for ch in self.picks if ch not in canales]

    def tiempo_frecuencia(self) -> np.ndarray:
        """Calcula el módulo de la Transformada Rápida de Fourier (FFT) sobre el eje del tiempo."""
        if self.data.size == 0:
            raise ValueError("No hay datos cargados para computar la representación espectral.")
        return np.abs(np.fft.fft(self.data, axis=-1))

    def obtener_mapeo_id_evento(self) -> Dict[int, str]:
        """Devuelve un diccionario estructurado mapeando cada id_evento a una etiqueta legible."""
        if self._eventos_raw.size == 0:
            return {}
        ids_unicos = set([int(ev[1]) for ev in self._eventos_raw])
        return {id_ev: f"Evento {id_ev}" for id_ev in ids_unicos}
    
    def cambiar_id_eventos(self, mapeo: Dict[int, int]):
        """Modifica dinámicamente los valores numéricos de los id_eventos en el origen de datos."""
        if self._eventos_raw.size == 0:
            return
            
        # Modificación polimórfica según la procedencia del dato original
        if isinstance(self.eventos, np.ndarray):
            for i in range(len(self.eventos)):
                self.eventos[i, 1] = mapeo.get(self.eventos[i, 1], self.eventos[i, 1])
            self._eventos_raw = self.eventos
        elif isinstance(self.eventos, Eventos):
            nuevos = []
            for muestra, id_ev in self.eventos.eventos:
                nuevos.append((muestra, mapeo.get(id_ev, id_ev)))
            self.eventos.eventos = nuevos
            self._eventos_raw = np.array(nuevos)

    # --- Dunders ---

    def __len__(self) -> int:
        return len(self.data) if self.data.size > 0 else 0

    def __str__(self) -> str:
        if self.data.size == 0:
            return "Epocas: Sin datos (0 épocas)"
        return f"Epocas: {len(self)} épocas, {self.data.shape[1]} canales, {self.data.shape[2]} muestras"