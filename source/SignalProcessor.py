#Clase SignalProcessor

import numpy as np

from source.RawSignal import RawSignal

#from source.RawSignal import RawSignal

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
        #Filtrado por canal
        filtrada = np.array([np.convolve(canal, kernel, mode = 'same') for canal in self.signal.data])
        return RawSignal(info=self.signal.info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=filtrada,first_samp=self.signal.first_samp)
    
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
        #Restamos componente lenta
        filtrada = (self.signal.data - lowpass.data)
        return RawSignal(info=self.signal.info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=filtrada,first_samp=self.signal.first_samp)
        
    def apply_notch(self, freq: float = 50):
        """
        Filtro para frecuancia epecífica de 50Hz.

        Parámetros
        ----------

        freq : float  #Frecuecnia a eliminar

        Returns
        -------

        Señal filtrada
        """

        #Frecuencia de muestreo
        fs = self.signal.info.frecuancia_muestreo
        #Frecuencia normalizada
        f0 = freq / fs
        #Coeficientes del filtro notch
        b = [1, -2*np.cos(2*np.pi*f0), 1]
        a = [1, -2*np.cos(2*np.pi*f0), 1]
        #Aplicamos el filtro por canal
        filtrada = np.array([np.convolve(canal, b, mode='same') for canal in self.signal.data])
        return RawSignal(info=self.signal.info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=filtrada,first_samp=self.signal.first_samp)   

    #:::::::::::::::::::::::::::
    # Métodos de normalización
    # ::::::::::::::::::::::::::

    def normalize(self):
        """
        Normaliza la señal en el rango [0,1] por canal.
        
        Returns
        -------
        Señal normalizada
        """
        data = self.signal.data

        minimo = np.min(data)
        maximo = np.max(data)

        normalizada = (data - minimo) / (maximo - minimo)
        return RawSignal(info=self.signal.info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=normalizada,first_samp=self.signal.first_samp)

    #::::::::::::::::::::::
    #Métods de remuestreo
    #::::::::::::::::::::::

    def resample(self, nueva_fs: float):
        """
        Remuestrea la señal a una nueva frecuencia de muestreo.
        
        Parámetros
        ----------
        
        nueva_fs : float  #Nueva frecuencia de muestreo en Hz.
        
        Returns
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
        nueva_info = self.signal.info
        nueva_info.frecuencia_muestreo = nueva_fs
        return RawSignal(info=nueva_info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones, data=remuestreada, first_samp=self.signal.first_samp)   
    
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

        #Obtenemos componente lenta
        lowpass = self.apply_lowpass(ventana=500) #Ventana grande para capturar tendencia lenta
        #Restamos componente lenta para eliminar línea base
        corregida = np.array([canal - np.mean(canal) for canal in self.signal.data])
        return RawSignal(info=self.signal.info, eventos=self.signal.eventos, anotaciones=self.signal.anotaciones,data=corregida,first_samp=self.signal.first_samp)  
    
    #::::::::::::::::::::::::
    #Métodos de información    
    #::::::::::::::::::::::::

    def __str__(self):
        """
        Representación en string del procesador de señales.
        """
        return (f"SignalProcessor asociado a " f"{self.signal.n_channels()} canales")
    