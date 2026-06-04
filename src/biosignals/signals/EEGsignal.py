#### El siguiente codigo comentado es el ejemplo de Lucas para la clase EEGSignal, 
#### se basa en la clase RawSignal y ofrece métodos específicos para señales EEG, como la transformada de Hilbert. 
#### Se importan las funciones necesarias de scipy.signal y se hereda de RawSignal para mantener la estructura común de las señales.


# from fede.signals import RawSignal
# from fede.signals import ExtractorCaracteristicas
# from scipy.signal import hilbert

# class EEGSignal(RawSignal):
#     """
#     Clase especializada para representar señales EEG.
#     Hereda de RawSignal y puede incluir métodos específicos para EEG.
#     """

#     def __init__(self, data, info):
#         super().__init__(data, info)
#         self.hilbert = None  # Atributo para almacenar la transformada de Hilbert de la señal EEG
#         #Aquí podríamos agregar atributos específicos para EEG si es necesario

#     def getHilbert(self):
#         """
#         Método para obtener la transformada de Hilbert de la señal EEG.
#         Retorna la señal transformada utilizando la función hilbert de scipy.
#         """
#         self.hilbert = hilbert(self.data, axis=1)
#         return self.hilbert
    

# eeg = EEG()
# _ = eeg.getHilbert()
# eeg.

import numpy as np
import warnings
import matplotlib.pyplot as plt
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor
from src.biosignals.preprocesamiento.ExtraerCaracteristicas import ExtraerCaracteristicas
from src.biosignals.epocas.Epocas import Epocas
from src.biosignals.info.Info import Info

class EEGSignal(RawSignal):
    """
    Clase para representar, analizar y procesar señales de EEG.
    """
    def __init__(self, data, info: Info, eventos, anotaciones, first_samp=0, 
                 times=None, montage=None, ref_type='common', units='µV', 
                 subject_info=None, fecha=None):
        
        # 1. Llamada al constructor de la clase base (RawSignal)
        # RawSignal ya valida que data sea 2D y first_samp >= 0
        super().__init__(info, eventos, anotaciones, data, first_samp)
        
        # 2. Atributos específicos del estándar 4.3.2
        self.info.frecuencia_muestreo = info.frecuencia_muestreo # Aseguramos que la frecuencia de muestreo esté presente en info
        self.times = times if times is not None else np.arange(self.data.shape[1]) / self.info.frecuencia_muestreo
        self.montage = montage
        self.ref_type = ref_type
        self.units = units
        self.subject_info = subject_info # (Edad, sexo, ID, grupo, etc.)
        self.fecha = fecha
        self.filtros_aplicados = []
        self.is_filtered = False
        self.is_trialed = False # Por defecto RawSignal es continua (2D)
        

        # 3. Validaciones obligatorias del contrato
        self._validar_dimensiones_eeg()
        self._validar_consistencia_temporal()

    # --- MÉTODOS DE VALIDACIÓN ---

    def _validar_dimensiones_eeg(self):
        """Valida dimensiones 2D/3D y consistencia con el vector de tiempos."""
        # Validación de rango de datos (2D o 3D según el estándar)
        if self.data.ndim not in [2, 3]:
            raise ValueError(f"Error: Los datos deben ser 2D o 3D. Se recibió: {self.data.ndim}D")
        
        # Validación: Longitud de tiempos == Longitud de muestras
        n_muestras = self.data.shape[-1]
        if len(self.times) != n_muestras:
            raise ValueError(f"Inconsistencia: El vector de tiempos ({len(self.times)}) "
                             f"no coincide con las muestras ({n_muestras})")

    def _validar_consistencia_temporal(self):
        """Lanza un warning si hay desfasaje entre fs y el vector temporal."""
        if len(self.times) > 1:
            dt_real = np.mean(np.diff(self.times))
            dt_esperado = 1.0 / self.info.frecuencia_muestreo
            if not np.isclose(dt_real, dt_esperado, atol=1e-5):
                warnings.warn(f"WARNING: El intervalo temporal entre muestras ({dt_real:.6f}s) "
                              f"no coincide con la frecuencia de muestreo ({self.info.frecuencia_muestreo}Hz).")

    # --- MÉTODOS QUE RETORNAN NUEVAS INSTANCIAS (INMUTABILIDAD) ---

    def get_channels(self, names: list[str]):
        """Retorna una nueva instancia de EEGSignal con los canales seleccionados."""
        indices = [self.info.nombre_canales.index(name) for name in names]
        new_data = self.data[indices, :]
        
        # Creamos una copia profunda de info para modificar nombres/tipos sin afectar al padre
        import copy
        new_info = copy.deepcopy(self.info)
        new_info.nombre_canales = [self.info.nombre_canales[i] for i in indices]
        new_info.tipo_canales = [self.info.tipo_canales[i] for i in indices]

        return EEGSignal(new_data, new_info, self.eventos, self.anotaciones, 
                         self.first_samp, times=self.times, subject_info=self.subject_info)

    def crop(self, tmin: float, tmax: float):
        """Retorna una nueva instancia de EEGSignal recortada temporalmente."""
        fs = self.info.frecuencia_muestreo
        inicio = int(tmin * fs)
        fin = int(tmax * fs)
        
        new_data = self.data[:, inicio:fin]
        new_times = self.times[inicio:fin]
        new_first_samp = self.first_samp + inicio

        return EEGSignal(new_data, self.info, self.eventos, self.anotaciones, 
                         new_first_samp, times=new_times, subject_info=self.subject_info)

    # --- PROCESAMIENTO USANDO SignalProcessor ---

    def apply_filter_eeg(self, l_freq=None, h_freq=None):
        """
        Aplica filtros usando el motor de SignalProcessor.
        """
        processor = SignalProcessor(self)
        temp_signal = self
        
        if l_freq:
            temp_signal = processor.apply_highpass(ventana=int(self.info.frecuencia_muestreo/l_freq))
            self.filtros_aplicados.append({'type': 'highpass', 'freq': l_freq})
        
        if h_freq:
            temp_signal = processor.apply_lowpass(ventana=int(self.info.frecuencia_muestreo/h_freq))
            self.filtros_aplicados.append({'type': 'lowpass', 'freq': h_freq})
            
        self.data = temp_signal.data
        self.is_filtered = True
        return self

    # --- INTEGRACIÓN CON CLASE EPOCAS ---

    def get_epochs(self, tmin=-0.2, tmax=0.5):
        """
        Segmenta la señal y retorna una instancia de la clase Epocas.
        """
        # Aquí se pasaría self.eventos.mapeo si existiera esa estructura en tu clase Eventos
        return Epocas(signal=self, eventos=self.eventos, tmin=tmin, tmax=tmax)

    # --- MÉTODOS DE ANÁLISIS ---

    def describe_eeg(self):
        """Características descriptivas avanzadas por canal."""
        stats = {}
        for i, name in enumerate(self.info.nombre_canales):
            ch_data = self.data[i, :]
            stats[name] = {
                "mean": np.mean(ch_data),
                "std": np.std(ch_data),
                "max": np.max(ch_data),
                "min": np.min(ch_data)
            }
        return stats

    

    def plot_spectrogram(self, ch_name):
        """
        Método solicitado: Calcula y genera una gráfica tiempo-frecuencia 
        para un canal en particular.
        """
        extractor = ExtraerCaracteristicas(self)
        f, t, Sxx = extractor.get_spectrogram(ch_name)
        
        plt.figure(figsize=(10, 5))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.title(f"Espectrograma (Tiempo-Frecuencia) - Canal: {ch_name}")
        plt.ylabel("Frecuencia [Hz]")
        plt.xlabel("Tiempo [seg]")
        plt.colorbar(label="Potencia (dB)")
        plt.show()

    def plot_hilbert(self, picks=None):
        """
        Método solicitado: Calcula y grafica la transformada de Hilbert 
        para uno o más canales.
        """
        extractor = ExtraerCaracteristicas(self)
        envelope = extractor.get_hilbert_transform(picks=picks)
        
        plt.figure(figsize=(10, 5))
        # Graficamos el sobre (envelope) sobre la señal original (opcionalmente)
        plt.plot(self.times, envelope.T)
        plt.title("Transformada de Hilbert (Envolvente de Amplitud)")
        plt.xlabel("Tiempo [seg]")
        plt.ylabel("Amplitud")
        plt.show()

    def plot_fft(self):
        """
        Método solicitado: Calcula y grafica el espectro de Fourier de la señal.
        """
        extractor = ExtraerCaracteristicas(self)
        freqs, fft_values = extractor.getFourierTransform()
        
        plt.figure(figsize=(10, 5))
        plt.plot(freqs, fft_values.T)
        plt.title("Espectro de Fourier (Magnitud)")
        plt.xlabel("Frecuencia [Hz]")
        plt.ylabel("Amplitud")
        plt.xlim(0, self.info.frecuencia_muestreo / 2) # Límite de Nyquist
        plt.show()