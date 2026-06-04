#Clase EMGSignal

import numpy as np
import matplotlib.pyplot as plt
from src.biosignals.signals import RawSignal
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import  Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

class EMGSignal(RawSignal):
    """
    Representa una señal electromiográfica(EMG).
    Hereda de RawSignal y agrega métodos específicos para procesamiento de señales EMG.
    La señal debe tener forma: canales x muestras.
    """
    def __init__(self,info: Info, eventos: Eventos, anotaciones: Anotaciones, data: np.ndarray, first_samp: int):
        """
        Inicializa una señal EMG.

        Parámetros
        ----------
        info : Info  #Información de adquisición.
        eventos : Eventos  #Eventos asociados a la señal
        anotaciones : Anotaciones  #Anotaciones de la señal
        data : np.ndarray  #Señal con forma: canales x muestras
        first_samp : int  #Ïndice de la primera muestra
        """
        #Constructor de RawSignal
        super().__init__(info,eventos,anotaciones,data,first_samp)
        #Atributos propios de EMG
        #Activación muscular detectada
        self.activacion_muscular = None
        #Valor RMS de la señal
        self.valor_rms = None
        #Envolvente EMG
        self.envolvente = None

    #::::::::::::::::::::::::::
    #Métodos de procesamiento
    #::::::::::::::::::::::::::

    def calcular_rms(self):
        """
        Calcula el valor RMS de la señal EMG para cada canal.
        
        Returns
        -------
        float  #Valor RMS calculado para cada canal.
        """
        
        #Fórmula RMS: sqrt(promedio(x^2))
        self.valor_rms = np.sqrt(np.mean(self.data**2, axis=1))
        return self.valor_rms

    def calcular_envolvente(self, ventana: int = 100):
        """
        Calcula la envolvente de la señal EMG utilizando una ventana móvil.

        EL cálcuoli se realiza mediante: rectifiación y suavizado por media móvil.

        Parámetros
        ----------
        ventana : int  #Tamaño de la ventana para el suavizado en muestras.
        Returns
        -------
        np.ndarray  #Envolvente calculada para cada canal.
        """

        #Rectificación de la señal
        rectificada = np.abs(self.data)
        #Kernel de media móvil
        kernel = np.ones(ventana) / ventana

        #Aplicamos convolución canal por canal para obtener la envolvente suavizada
        self.envolvente = np.array([np.convolve(canal, kernel, mode='same') for canal in rectificada])
        return self.envolvente
    
    def detectar_activacion(self, umbral: float):
        """
        Detecta activación muscular.
        
        Parámetros
        ----------
        umbral : float  #Valor umbral para detectar activación.

        Returns
        -------
        np.ndarray  #Matriz booleana indicando activación (True) o no activación (False) para cada canal y muestra.
        """
        #Detectamos muestras cuya amplitud supera el umbral
        self.activacion_muscular = (self.data > umbral)
        return self.activacion_muscular

    #::::::::::::::::::::::::::
    #Métodos de visualización
    #::::::::::::::::::::::::::

    def plot_envolvente(self):
        """
        Grafica la envolvente EMG
        """
        #Verificamos que exista envolvente
        if self.envolvente is None:
            raise ValueError("No se ha calculado la envolvente")
        #Graficamos
        plt.plot(self.envolvente.T)

        plt.title("Envolvente EMG")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")
        plt.show()

    #:::::::::::::::::::::::::
    #Métodos de Información
    #:::::::::::::::::::::::::
    
    def resumen_emg(self):
        """
        Muestra información resumida de la señal EMG.
        """
        
        print("Resumen EMG")
        print("--------------")
        print(f"Canales: {self.n_channels()}")
        print(f"Muestras: {self.n_samples()}")
        print(f"Duración: {self.duration():.2f} segundos")
        
        #Mostramos RMS si existe
        if self.valor_rms is not None:
            print(f"RMS: {self.valor_rms:.4f}")
            
    def __str__(self):
        """
        Representación textual del objeto EMGSignal.
        """
        return (f"EMGSignal : " f"{self.n_channels()} canales," f"{self.n_samples()} muestras, "f"duración {self.duration():.2f} s")
    
    
