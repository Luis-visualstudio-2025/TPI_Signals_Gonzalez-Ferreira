## ExtraerCaracteristicas.py "version no final", se ha creado para proporcionar funcionalidades de extracción de características a partir de señales crudas. 
# Esta clase se basa en la clase RawSignal y ofrece métodos para calcular métricas estadísticas, transformadas de Hilbert, espectrogramas y transformadas de Fourier.
import numpy as np
from scipy.signal import hilbert, spectrogram
from Biosignals.Signals.RawSignal import RawSignal

class ExtraerCaracteristicas:
    """
    Clase encargada de extraer métricas y transformadas de una señal.
    Trabaja con objetos de tipo RawSignal o derivados.
    """
    raw=RawSignal() #Esto es solo para que no tire error, se debe pasar un objeto RawSignal al crear una instancia de ExtraerCaracteristicas
    raw.get_data() #Esto es solo para que no tire error, se debe pasar un objeto RawSignal al crear una instancia de ExtraerCaracteristicas
    
    def __init__(self, signal):
        self.signal = signal
        self.caracteristicas = {}
       

    def signals(self):
        """Retorna la señal original."""
        return self.signal.data
    
    def mean(self):
        """Calcula la media por canal."""
        return np.mean(self.signal.data, axis=1)

    def std(self):
        """Calcula la desviación estándar por canal."""
        return np.std(self.signal.data, axis=1)

    def get_hilbert_transform(self, picks=None):
        """
        Calcula la transformada de Hilbert para obtener la amplitud instantánea.
        """
        # Obtenemos los datos (todos o una selección)
        data = self.signal.get_data(picks=picks)
        
        # Aplicamos la transformada de Hilbert por canal
        # La amplitud instantánea es el valor absoluto de la señal analítica
        analytic_signal = hilbert(data)
        amplitude_envelope = np.abs(analytic_signal)
        
        return amplitude_envelope

    def get_spectrogram(self, ch_name):
        """
        Calcula la representación Tiempo-Frecuencia para un canal específico.
        """
        # Obtenemos los datos del canal solicitado
        data = self.signal.get_channels([ch_name])[0] # Tomamos el primer (y único) canal
        fs = self.signal.info.frecuencia_muestreo
        
        # Calculamos el espectrograma (Tiempo-Frecuencia)
        f, t, Sxx = spectrogram(data, fs)
        
        return f, t, Sxx

    def getFourierTransform(self):
        """Calcula la FFT de la señal."""
        fs = self.signal.info.frecuencia_muestreo
        data = self.signal.data
        n = data.shape[1]
        
        freqs = np.fft.rfftfreq(n, d=1/fs)
        fft_values = np.abs(np.fft.rfft(data, axis=1))
        
        return freqs, fft_values