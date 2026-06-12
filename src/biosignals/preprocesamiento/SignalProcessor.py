#Clase SignalProcessor

import numpy as np
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.info.Info import Info 
import copy

class SignalProcessor:
    """
    Clase encargada del proccesamietno digital de señales biomédicas.
    Trabaja sobre objetos RaewSignal o clases derivadas.
    La clase NO MODIFICA la señal original.
    Cada método retorna una señal nueva procesada.
    """
    def __init__(self, signal: RawSignal):
        """
        Inicializa el procesor de señales.
        Parámetros
        ----------
        signal : RawSignal  #Señal biomédica a procesar.
        """
        self.signal = signal

    #:::::::::::::::::::::
    #Métodos de filtrado
    #:::::::::::::::::::::

    def apply_lowpass(self, ventana: int = 5):
        """
        Aplica un filtro pasabajos mediante media móvil
        Parámetros
        ----------
        ventana : int  #Tamaño de la ventana del filtro en muestras.
        Returns
        -------
        Nueva señal filtrada
        """
        #Kernel de media móvil
        kernel = np.ones(ventana) / ventana
        if ventana <= 0:
            raise ValueError("ventana debe ser positiva")
        #Filtrado por canal
        filtrada = np.array([np.convolve(canal, kernel, mode = 'same') for canal in self.signal.data])
        nueva_info = copy.deepcopy(self.signal.info)
        return self.signal.__class__(info=nueva_info,eventos=self.signal.eventos,anotaciones=self.signal.anotaciones,data=filtrada,first_samp=self.signal.first_samp)
    
    def apply_highpass(self, ventana: int = 5):
        """
        Aplica un filtro pasaltos.
        Se calcula : señal original - pasabajos
        Parámetros
        ----------
        ventana : int  #Tamaño de la ventana del filtro en muestras.
        Returns
        -------
        Nueva señal filtrada
        """
        #Obtenemos componente lenta
        lowpass = self.apply_lowpass(ventana)
        if ventana <= 0:
            raise ValueError("ventana debe ser positiva")
        #Restamos componente lenta
        filtrada = (self.signal.data - lowpass.data)
        nueva_info = copy.deepcopy(self.signal.info)
        return self.signal.__class__(info=nueva_info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=filtrada,first_samp=self.signal.first_samp)
        
    def apply_notch(self, freq: float = 50, Q: float = 30):
        """
        Filtro para frecuencia epecífica de 50Hz.
        Parámetros
        ----------
        freq : float  #Frecuecnia a eliminar
        Q : float #Factor de calidad del filtro, valores altos -> notch más estrecho
        Retorna
        -------
        Señal filtrada
        """
        from scipy.signal import iirnotch
        from scipy.signal import filtfilt
        import copy
    
        #Frecuencia de muestreo
        fs = self.signal.info.frecuencia_muestreo
        #Validaciones
        if freq <= 0:
            raise ValueError("La frecuencia debe ser positiva")
        if freq >= fs/2:
            raise ValueError("La frecuencia debe cumplir con el criterio de Nyquist")
        if Q <= 0:
            raise ValueError("Q debe ser positivo")

        #Diseño del filtro notch
        b,a = iirnotch(w0=freq, Q=Q, fs=fs)
        #Aplicación canal por canal
        filtrada = np.array([filtfilt(b,a,canal) for canal in self.signal.data])
        nueva_info = copy.deepcopy(self.signal.info)

        return self.signal.__class__(info = nueva_info, eventos = self.signal.eventos, anotaciones = self.signal.anotaciones, data = filtrada, first_samp = self.signal.first_samp)
      
    #:::::::::::::::::::::::::::
    # Métodos de normalización
    # ::::::::::::::::::::::::::

    def normalize(self):
        """
        Normaliza la señal en el rango [0,1] por canal.
        Retorna
        -------
        Señal normalizada
        """
        data = self.signal.data
        minimo = np.min(data, axis=1, keepdims=True)
        maximo = np.max(data, axis=1, keepdims=True)
        normalizada = (data - minimo) / (maximo - minimo)
        nueva_info = copy.deepcopy(self.signal.info)
        return self.signal.__class__(info=nueva_info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=normalizada,first_samp=self.signal.first_samp)

    #::::::::::::::::::::::
    #Métods de remuestreo
    #::::::::::::::::::::::

    def resample(self, nueva_fs: float):
        """
        Remuestrea la señal a una nueva frecuencia de muestreo.
        Parámetros
        ----------
        nueva_fs : float  #Nueva frecuencia de muestreo en Hz.
        Retorna
        -------
        Señal remuestreada
        """
        old_fs = (self.signal.info.frecuencia_muestreo)
        factor = nueva_fs / old_fs
        #Calculamos nuevo número de muestras
        n_muestras = int(self.signal.n_samples() * factor)
        #Remuestreamos por canal
        remuestreada = np.array([np.interp(np.linspace(0, self.signal.n_samples(), n_muestras), np.arange(self.signal.n_samples()), canal) for canal in self.signal.data])
        #Actualizamos info de la señal
        nueva_info = copy.deepcopy(self.signal.info)
        nueva_info.frecuencia_muestreo = nueva_fs
        return self.signal.__class__(info=nueva_info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones, data=remuestreada, first_samp=self.signal.first_samp)   
    
    #:::::::::::::::::::::::
    #Métodos de corrección
    #:::::::::::::::::::::::

    def remove_baseline(self):
        """
        Elimina la línea base de la señal.
        Returns
        -------
        Señal con línea base eliminada
        """
        #Restamos componente lenta para eliminar línea base
        corregida = np.array([canal - np.mean(canal) for canal in self.signal.data])
        nueva_info = copy.deepcopy(self.signal.info)
        return self.signal.__class__(info=nueva_info.signal.info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=corregida,first_samp=self.signal.first_samp)  
    
    #::::::::::::::::::::::::
    #Métodos de información    
    #::::::::::::::::::::::::

    def __str__(self):
        """
        Representación en string del procesador de señales.
        """
        return (f"SignalProcessor asociado a " f"{self.signal.n_channels()} canales")
    