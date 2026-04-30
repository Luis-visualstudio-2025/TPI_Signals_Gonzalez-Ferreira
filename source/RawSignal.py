#Clase RawSignal

import numpy as np
import matplotlib.pyplot as plt

class RawSignal:
    def __init__(self,info:Info,eventos:Eventos,anotaciones:Anotaciones,data:np.ndarray,first_samp:int):
        self.info = info      #contiene datos
        self.eventos = eventos #objeto eventos
        self.anotaciones = anotaciones #objeto anotaciones
        #self.sfreq = sfreq #puede que se redundante si fs está en Info sacarlo del UML
        self.data = data #señal en formateo numpy si uso _data muestra que es interno pero voy a dejarlo coomo data por ahora
        self.first_samp = first_samp #primera muestra,offfset

#Métodos de la clase RawSignal
    #métodos básicos
    def n_samples(self):
    #devolvemos la canidad de columnas (muestras)
        return self.data.shape[1]

    def n_channels(self):
    #devolvemos la cantidad de filas(canales)
        return self.data.shape[0]

    def duration(self):
    #calculo la duración en segundos
        fs = self.info.frecuencia_muestreo
        return self.n_samples()/fs

    #métodos para acceso a datos
    def get_data(self, picks = None): #(si no especifico canales devuelve todo)
        if picks is None:
            return self.data
    #picks por nombre
        indices = [self.info.nombres_canales.index(ch) for ch in picks]
        return self.data[indices]
    def __getitem__(self, item):
        return self.data[item] #me permite hacer raw[0] o raw[:, 100:200]
    
    #métodos para canales
    def get_channels(self, names: list):
        indices = []

        for name in names:
            idx = self.info.nombres_canales.index(name)
            indices.append(idx)
        return self.data[indices]
  

    def drop_channels(self,names:list):
        indices = []
        for name in names:
            idx = self.info.nombres_canales.index(name)
            indices.append(idx)
    #creo una lista de canales que voy a mantener
        keep = [i for i in range(self.n_channels()) if i not in indices]

        self.data = self.data[keep]
        self.info.nombres_canales = [self.info.nombres_canales[i] for i in keep]

    def picks_types(self, tipo : str):
        indices = []
        for i, t in enumerate(self.info.tipos_canales):
            if t == tipo:
                indices.append(i)
        self.data = self.data[indices]
        self.info.nombres_canales = [self.info.nombres_canales[i] for i in indices]
        self.info.tipos_canales = [self.info.tipos_canales[i] for i in indices]

    #métodos para procesamiento
    def filter(self, tipo ="media", ventana =5):
        if tipo == "media":
            kernel = np.ones(ventana)/ventana
            self.data = np.array([
                np.convolve(canal, kernel, mode = 'same')
                for canal in self.data
                ])

    def crop(self, tmin: float, tmax : float):
        fs = self.info.frecuencia_muestreo
        inicio = int(tmin*fs)
        fin = int(tmax*fs)
        self.data = self.data[:, inicio:fin]
        self.first_samp += inicio

    #métodos para anotaciones
    def set_anotaciones(self, anotaciones):
        self.anotaciones = anotaciones

    #métodos para visualización
    def plot(self):
        plt.plot(self.data.T)
        plt.title("Raw Signal")
        plt.xlabel("Muestraas")
        plt.ylabel("Amplitud")
        plt.show()
    
    #métodos para información de raw
    def describe(self):
        return{"n_canales": self.n_channels(), "n_muestras": self.n_samples(), "duración": self.duration(),"fs":self.info.frecuencia_muestreo}
    
    def resumen(self):
        print("Resumen de la señal:")
        print(f"Canales:{self.n_channels()}")
        print(f"Muestras:{self.n_samples()}")
        print(f"Duración:{self.duration():.2f} s")
        print(f"Frecuencia de muestreo: {self.info.frecuencia_muestreo} Hz")

    def __str__(self):
        return f"RawSignal : {self.n_channels()} canales, {self.n_samples()} muestras, duración {self.duration():.2f} s"
    











