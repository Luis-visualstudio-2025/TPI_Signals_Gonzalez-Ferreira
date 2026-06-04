#Clase RawSignal

import numpy as np
import matplotlib.pyplot as plt
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

class RawSignal:
    
    """
    Representa una señal biomédica multicanal
    """
    
    def __init__(self,info:Info,eventos:Eventos,anotaciones:Anotaciones,data:np.ndarray,first_samp:int):

        """
        Inicializa un objeto RawSignal.

        Parámetros
        ----------
        info : Info  #Información de la adquisición
        eventos : Eventos  #Eventos asociados a la señal
        anotaciones : Anotaciones  #Anotaciones de la señal
        data : np.ndarray  #Matriz con forma de cnales x muestras
        first_samp : int  #Índice de la primera mustra.
        """
        
        #Contrato:
        #data debe ser una matriz 2D con forma de canales x muesstras
        #first_samp no puede ser negativo

        if data.ndim != 2:
            raise ValueError("data debe tener forma de canales x muestras")
        
        if first_samp < 0:
            raise ValueError("first_samp no puede ser negativo")
        
        #Guardamos atributos del objeto
        
        self.info = info #contiene datos
        self.eventos = eventos #objeto eventos
        self.anotaciones = anotaciones #objeto anotaciones
        self.data = data #señal en formateo numpy si uso _data muestra que es interno pero voy a dejarlo coomo data por ahora
        self.first_samp = first_samp #primera muestra,offfset

#Métodos de la clase RawSignal
    #::::::::::::::::::::::::::
    #Métodos básicos
    #::::::::::::::::::::::::::

    def n_samples(self) -> int:
        """
        Retorna la cantidad de muestras de la señal
        """
        return self.data.shape[1]

    def n_channels(self):
        """
        Retorna la cantidad decanales de la señal
        """
        return self.data.shape[0]

    def duration(self) -> float:
        """
        Calcula la duración total de la señal en segundos
        """
        fs = self.info.frecuencia_muestreo
        return self.n_samples()/fs

    #:::::::::::::::::::::::::::
    #Métodos de acceso a datos
    #:::::::::::::::::::::::::::

    def get_data(self, picks = None): 
        """
        Retorna los datos de la señal.

        Parámetros
        ----------
        picks : list[str] #Lista de nombres de canales a seleccionar.

        Returns
        -------
        np.ndarray #Matriz de datos de la señal
        """
        #Si no se epecifican canales, se devuelve toda la señal
        if picks is None:
            return self.data
        
        #Obtenemos índices de canales seleccionados
        indices = [self.info.nombre_canales.index(ch) for ch in picks]
        return self.data[indices]
    
    def __getitem__(self, item):
        """
        Permite acceder a los datos usando indexing.

        Ejemplo
        -------
        raw[0]
        raw[:, 100:200]
        """
        return self.data[item] 
    
    #::::::::::::::::::::::::::::::
    #Métodos de manejo de canales
    #::::::::::::::::::::::::::::::

    def get_channels(self, names: list[str]) -> np.ndarray:
        """
        Retorna los canales seleccionados.
        """
        indices = [self.info.nombre_canales.index(name)
                   for name in names]
        return self.data[indices]
  

    def drop_channels(self,names:list[str]):
        """
        Elimina cnaales de la señal
        """
        #Obtenemos ínidces de canales a eliminar
        indices = [self.info.nombre_canales.index(name)
                   for name in names]
        
        #Obtengo índices de canales a conservar
        keep = [i for i in range(self.n_channels()) if i not in indices]

        #Actualizo datos
        self.data = self.data[keep]
        #Actualizo cnaales
        self.info.nombre_canales = [self.info.nombre_canales[i] for i in keep]

    def picks_types(self, tipo : str):
        """
        Seleccona canales según su tipo
        """
        indices = [i for i, t in enumerate(self.info.tipos_canales)
                   if t == tipo]
        
        #Actualizo datos
        self.data = self.data[indices]

        #Actulizo nombres de canales
        self.info.nombre_canales = [self.info.nombre_canales[i] for i in indices]

        #Actualizo tipos de canales
        self.info.tipos_canales = [self.info.tipos_canales[i] for i in indices]

    #::::::::::::::::::::::::::
    #Métodos de procesamiento
    #::::::::::::::::::::::::::

    def filter(self, tipo: str = "media", ventana: int = 5):
        """
        Aplica un filtro simple a la señal

        Parámetros
        ----------
        tipo : str  #Tipo de filtro.
        ventana : int  #Tamaño de ventana del filtro.
        """
        #Filtro de media móvil
        if tipo == "media":
            #Kernel del filtro
            kernel = np.ones(ventana)/ventana
            #Aplico convolución a cada canal
            self.data = np.array([np.convolve(canal, kernel, mode = 'same') for canal in self.data])

    def crop(self, tmin: float, tmax : float):
        """
        Recorta la señal entre tmin y tmax segundos.
        """
        #Contrato:
        #tmin debe ser menor que tmax
        if tmin >= tmax:
            raise ValueError("tmin deber ser menor que tmax")
        #Frecuencia de muestreo
        fs = self.info.frecuencia_muestreo
        #Convierto segundos a muestras
        inicio = int(tmin*fs)
        fin = int(tmax*fs)
        #Recroto la señal
        self.data = self.data[:, inicio:fin]
        #Actualizo la primera muestra
        self.first_samp += inicio

    #::::::::::::::::::::::::
    #Métodos de anotaciones
    #::::::::::::::::::::::::

    def set_anotaciones(self, anotaciones: Anotaciones):
        """
        Actualiza las anotacionees de la señal.
        """
        self.anotaciones = anotaciones

    #::::::::::::::::::::::::::
    #Métodos de visualización
    #::::::::::::::::::::::::::

    def plot(self, picks: list[str] = None):
        """
        Grafica la señal.
        """
        #Obtengo los datos seleccionados
        data = self.get_data(picks)
        #Grafico canales
        plt.plot(self.data.T)
        plt.title("Raw Signal")
        plt.xlabel("Muestraas")
        plt.ylabel("Amplitud")
        plt.show()
    
    #::::::::::::::::::::::
    #Métodos informativos
    #::::::::::::::::::::::

    def describe(self):
        """"
        Retorna información resumida de la señal
        """
        return{"n_canales": self.n_channels(), "n_muestras": self.n_samples(), "duración": self.duration(),"fs":self.info.frecuencia_muestreo}
    
    def resumen(self):
        """
        Imprime un resumen de la señal
        """
        print("Resumen de la señal:")
        print(f"Canales:{self.n_channels()}")
        print(f"Muestras:{self.n_samples()}")
        print(f"Duración:{self.duration():.2f} s")
        print(f"Frecuencia de muestreo: {self.info.frecuencia_muestreo} Hz")

    def __str__(self):
        """
        Representación en texto del objeto.
        """
        return (f"RawSignal : {self.n_channels()} canales, {self.n_samples()} muestras, duración {self.duration():.2f} s")
    

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#Fin de RawSignal (de momento)                                                                                                                                                                                                                                                                                                                       ::
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::   











