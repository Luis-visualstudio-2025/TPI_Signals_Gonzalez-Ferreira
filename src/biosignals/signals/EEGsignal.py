#Clase EEGSignal
import numpy as np
import warnings
import matplotlib.pyplot as plt
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor
from src.biosignals.preprocesamiento.ExtraerCaracteristicas import ExtraerCaracteristicas
from src.biosignals.epocas.Epocas import Epocas
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import  Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

class EEGSignal(RawSignal):
    """
    Clase para representar, analizar y procesar señales de EEG.
    """
    def __init__(self,info: Info, eventos: Eventos, anotaciones: Anotaciones,data: np.ndarray, first_samp=0, 
                 times=None, montage=None, ref_type='common', units='µV', 
                 subject_info=None, fecha=None):
        
        #1. Llamada al constructor de la clase base (RawSignal)
        #RawSignal ya valida que data sea 2D y first_samp >= 0
        super().__init__(info, eventos, anotaciones, data, first_samp)
        
        #2. Atributos específicos del estándar
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
        if self.data.ndim != 2:
            raise ValueError("EEGSignal debe contener datos continuos 2D (canales x muestras)")
        if len(self.times) != self.data.shape[1]:
            raise ValueError("El vector temporal no coincide con las muestras")
        
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


    def picks_channels(self, names: list[str]):
        #"""Retorna una nueva instancia de EEGSignal con los canales seleccionados."""
        import copy
        for name in names:
            if name not in self.info.nombre_canales:
                raise ValueError(f"Canal {name} no existe")
        indices = [self.info.nombre_canales.index(name)
                   for name in names]
        new_data = self.data[indices, :]
        new_info = copy.deepcopy(self.info)
        new_info.nombre_canales = [self.info.nombre_canales[i] for i in indices]
        new_info.tipos_canales = [self.info.tipos_canales[i] for i in indices]

        return EEGSignal(new_info, self.eventos, self.anotaciones, new_data, self.first_samp, times=self.times, subject_info=self.subject_info)

    def crop(self, tmin: float, tmax: float):
        """Retorna una nueva instancia de EEGSignal recortada temporalmente."""
        import copy
        if tmin >= tmax:
            raise ValueError("tmin debe ser menor que tmax")
        if tmin <0:
            raise ValueError("tmin ni puede ser negativo")
        if tmax > self.duration():
            raise ValueError("tmax excede la duración")
        
        fs = self.info.frecuencia_muestreo
        inicio = int(tmin * fs)
        fin = int(tmax * fs)
        
        new_data = self.data[:, inicio:fin]
        new_times = self.times[inicio:fin]
        new_first_samp = self.first_samp + inicio
        new_info = copy.deepcopy(self.info)
        return EEGSignal(new_info, self.eventos, self.anotaciones, new_data, new_first_samp, times=new_times, subject_info=self.subject_info)

    # --- PROCESAMIENTO USANDO SignalProcessor ---

    def apply_filter_eeg(self, l_freq=None, h_freq=None):
        """
        Aplica filtros usando el motor de SignalProcessor.
        """
        import copy
        processor = SignalProcessor(self)
        temp_signal = self
        
        if l_freq:
            temp_signal = processor.apply_highpass(ventana=int(self.info.frecuencia_muestreo/l_freq))
            self.filtros_aplicados.append({'type': 'highpass', 'freq': l_freq})
        
        if h_freq:
            temp_signal = processor.apply_lowpass(ventana=int(self.info.frecuencia_muestreo/h_freq))
            self.filtros_aplicados.append({'type': 'lowpass', 'freq': h_freq})
        
        new_info = copy.deepcopy(self.info)
            
        #self.data = temp_signal.data
        #self.is_filtered = True
        return EEGSignal(new_info, self.eventos, self.anotaciones, temp_signal.data,  self.first_samp, times=self.times, montage=self.montage,ref_type=self.ref_type,units=self.units,subject_info=self.subject_info,fecha=self.fecha)

    # --- INTEGRACIÓN CON CLASE EPOCAS ---

    def get_epochs(self, id_eventos = None, tmin=-0.2, tmax=0.5):
        """
        Segmenta la señal y retorna una instancia de la clase Epocas.
        """
        # Aquí se pasaría self.eventos.mapeo si existiera esa estructura en tu clase Eventos
        return Epocas(signal=self, eventos=self.eventos,id_eventos= id_eventos, tmin=tmin, tmax=tmax)

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
        plt.plot(self.times[:envelope.shape[1]],envelope.T)
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

    def __str__(self):
        return(f"EEGSignal: "f"{self.n_channels()} canales, "f"{self.n_samples()} muestras, "f"fs={self.info.frecuencia_muestreo} Hz")