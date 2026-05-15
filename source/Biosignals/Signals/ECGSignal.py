#Clase ECGSignal

import numpy as np
import matplotlib.pyplot as plt
from Biosignals.Signals.RawSignal import RawSignal
from Biosignals.Info.Info import Info
from Biosignals.Eventos.Eventos import  Eventos
from Biosignals.Eventos.Anotaciones import Anotaciones

class ECGSignal(RawSignal):
    """
    Representa una señal eñectrocardiográfica (ECG).
    Hereda de RawSignal y agrega métodos específicos para el procesamiento de señales ECG.
    La señal debe tener forma: canales x muestras.
    """
    def __init__(self, info: Info, eventos: Eventos, anotaciones: Anotaciones, data: np.ndarray, first_samp: int):

        """
        Inicializa una señal ECG.
        
        Parámetros
        ----------
        
        info : Info  #Información de adquisición
        eventos : Eventos  #Eventos asociados a la señal
        anotaciones : Anotaciones  #Anotaciones de la señal
        data : np.ndarray  #Señal con forma: canales x muestras
        first_samp : int  #índice de la primera muestra
        """
        #Constructor de RawSignal
        super().__init__(info,eventos,anotaciones,data,first_samp)
        #Atributos propios de ECG
        #Frecuencia cardíaca
        self.freq_cardiaca = None
        #Intervalos RR
        self.intervalos_rr = None
        #índices de picos R detectados
        self.picos = None
        #Arritmias detectadas
        self.arritmias = None
    
    #::::::::::::::::::::::::::
    #Métodos de procesamiento
    #::::::::::::::::::::::::::

    def detectar_picos(self, umbral: float):
        """
        Detecta picos R mediante umbral.
        
        Parámetros
        ----------
        
        umbral : float  #Umbral mínimo de amplitud
        
        Returns
        -------
        
        np.ndarray  #Índices de muestras donde hay picos
        """
        #Usamos el primer canal
        señal = self.data[0]

        picos = []

        #Recorremos evitando extremos
        for i in range(1, len(señal) - 1):
            #Máximo local + umbral
            if (señal[i] > señal[i - 1] and señal[i] > señal[i + 1] and señal[i] > umbral):
                picos.append(i)
        
        self.picos = np.array(picos)
        return self.picos
    
    def calcular_intervalos_rr(self):
        """
        Calcula intervalos RR en segundos.
        
        Returns
        -------
        
        np.ndarray  #Intervalos RR
        """

        #Verificamos que eisten picos
        if self.picos is None:
            raise ValueError("No se han detectado picos")

        fs = self.info.frecuencia_muestreo

        #Diferencia entre picos consecutivos
        self.intervalos_rr = np.diff(self.picos) / fs
        return self.intervalos_rr

    def calcular_freq_cardiaca(self):
        """
        Calcula la frecuecnia cardíaca a partir de intervalos RR:
        
        Returns
        -------
        
        float  #Frecuencia cardíaca en latidos por minuto
        """ 
        #Verificamos RR
        if self.intervalos_rr is None:
            raise ValueError("No se han calculado intervalos RR")
        rr_promedio = np.mean(self.intervalos_rr)
        self.freq_cardiaca = 60 / rr_promedio
        return self.freq_cardiaca
    
    def detectar_arritmias(self, rr_min: float = 0.6, rr_max: float = 1.2):
        """
        Detecta psoibles arritmias simples.
        
        Parámetros
        ----------
        
        rr_min : float  #Intervalo RR mínimo normal
        rr_max : float  #Intervalo RR máximo normal
        
        Returns
        -------
        
        np.ndarray  #Índices de intervalos normales.
        """
        #Verificamos RR
        if self.intervalos_rr is None:
            raise ValueError("No se han calculado intervalos RR")
        
        #Detectamos RR anormales
        self.arritmias = np.where((self.intervalos_rr < rr_min) | (self.intervalos_rr > rr_max))[0]
        return self.arritmias
    
    #::::::::::::::::::::::::::
    #Métodos de visualización
    #::::::::::::::::::::::::::

    def plot_ecg(self):
        """
        Grafica la señal de ECG
        """
        
        plt.plot(self.data[0])
        plt.title("Señal ECG")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")
        plt.show()

    def plot_picos(self):
        """
        Grafica señal ECG con picos detectasdos
        """

        #Verifico que existan picos
        if self.picos is None:
            raise ValueError("No se han detectado picos")
        
        señal = self.data[0]
        plt.plot(señal)

        #Marcamos los picos
        plt.plot(self.picos, señal[self.picos], 'ro')
        plt.title("ECG con picos R detectados")
        plt.xlabel("Muestras")
        plt.ylabel("Amplitud")
        plt.show()

    #::::::::::::::::::::::::
    #Métodos de información
    #::::::::::::::::::::::::

    def resumen_ecg(self):
        """
        Muestra información resumida de la señal ECG
        """

        print("Resumen de la señal ECG")
        print("-------------------------")

        print(f"Canales: {self.n_channels()}")
        print(f"Muestras: {self.n_samples()}")

        print(f"Duración:" f"{self.duration():.2f} segundos")

        if self.freq_cardiaca is not None:
            print(f"Frecuecnia cardíaca: "f"{self.freq_cardiaca:.2f} latidos por minuto")

        if self.intervalos_rr is not None:
            print(f"Cantidad de intervalos RR: "f"{len(self.intervalos_rr)}")

    def __str__(self):
        """
        Representación textual del objeto ECGSignal
        """
        return (f"ECGSignal: " f"{self.n_channels()} canales, "f"{self.n_samples()} muestras, "f"duración {self.duracion():.2f} segundos")
