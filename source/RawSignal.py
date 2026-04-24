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

def get_data(self, picks = None): #(si no especifico canales devuelve todo)
    if picks is None:
        return self.data
    #si picks es lista de indices
    return self.data[picks]
    
def get_channels(self, names: list):
    indices = []

    for name in names:
        idx = self.info.nombres_canales.index(name)
        indices.append(idx)
    self.data = self.data[indices]
    self.info.nombres_canales = names

def drop_channels(self,names:list):
    indices = []
    for name in names:
        idx = self.info.nombre_canales.index(name)
        indices.append(idx)
    #creo una lista de canales que voy a mantener
    keep = [i for i in range(self.n_channels()) if i not in indices]

    self.data = self.data[keep]
    self.info.nombres_canales = [self.info.nombres_canales[i] for i in keep]

def plot(self):
    plt.plot(self.data.T)
    plt.title("Raw Signal")
    plt.xlabel("Muestraas")
    plt.ylabel("Amplitud")
    plt.show()

def crop(self, tmin: float, tmax : float):
    fs = self.info.frecuencia_muestreo
    











