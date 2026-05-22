#Clase Épocas

import numpy as np
import matplotlib.pyplot as plt

from Biosignals.Signals.RawSignal import RawSignal
from Biosignals.Eventos.Eventos import Eventos


class Epocas:

    """
    Representa un conjunto de épocas obtenidas a partir de una señal biomédica y eventos.
    Cada época corresponde a un intervalo temporal alrededor de un evento.
    Forma de datos: (epocas x canales x muestras)
    """

    def __init__(self, signal: RawSignal, eventos: Eventos, id_eventos=None, tmin: float = -0.2, tmax: float = 0.5, picks=None,reject=None):
        """
        Inicializa el objeto Epocas.

        Parámetros
        ----------
        signal : RawSignal  #Señal biomédica original.
        eventos : Eventos  #Eventos asociados a la señal.
        id_eventos : list | None  #IDs de eventos a seleccionar.
        tmin : float  #Tiempo inicial relativo al evento.
        tmax : float  #Tiempo final relativo al evento.
        picks : list | None  #Canales seleccionados.
        reject : dict | None  #Criterios de rechazo.
        """

        self.signal = signal
        self.eventos = eventos
        self.id_eventos = id_eventos
        self.tmin = tmin
        self.tmax = tmax
        self.picks = picks
        self.reject = reject
        # Datos de épocas
        self.data = self._crear_epocas()

    #Métodos

    def _crear_epocas(self):

        """
        Genera las épocas a partir de eventos.

        Returns
        -------
        np.ndarray  #Datos con forma: (epocas x canales x muestras)
        """

        fs = self.signal.info.frecuencia_muestreo
        inicio = int(self.tmin * fs)
        fin = int(self.tmax * fs)
        eventos_lista = self.eventos.eventos
        epocas = []
        for muestra, id_evento in eventos_lista:
            #Filtrado opcional por IDs
            if (self.id_eventos is not None and id_evento not in self.id_eventos):
                continue

            inicio_epoca = muestra + inicio
            fin_epoca = muestra + fin

            #Verificamos límites válidos
            if (inicio_epoca < 0 or fin_epoca > self.signal.n_samples()):
                continue
            #Extraemos datos
            epoca = self.signal.data[:, inicio_epoca:fin_epoca]

            #Selección de canales
            if self.picks is not None:
                indices = [self.signal.info.nombres_canales.index(ch) for ch in self.picks]
                epoca = epoca[indices]
            epocas.append(epoca)
        return np.array(epocas)

    def get_data_Epoc(self):
        """
        Obtiene los datos de épocas.

        Returns
        -------
        np.ndarray  #Datos de épocas.
        """
        return self.data

    def promedio_Epoc(self):

        """
        Calcula el promedio de todas las épocas.

        Returns
        -------
        np.ndarray  #Promedio de épocas.
        """

        return np.mean(self.data, axis=0)

    def recortar_Epoc(self, tmin: float, tmax: float):
        """
        Recorta temporalmente las épocas.

        Parámetros
        ----------
        tmin : float  #Tiempo inicial.

        tmax : float  #Tiempo final.

        Returns
        -------
        np.ndarray  #Épocas recortadas.
        """

        fs = self.signal.info.frecuencia_muestreo
        inicio = int((tmin - self.tmin) * fs)
        fin = int((tmax - self.tmin) * fs)
        return self.data[:, :, inicio:fin]

    def eliminar_canales_Epoc(self, canales: list):
        """
        Elimina canales de las épocas.

        Parámetros
        ----------
        canales : list  #Canales a eliminar.
        """

        indices = [self.signal.info.nombres_canales.index(ch) for ch in canales]
        keep = [i for i in range(self.data.shape[1]) if i not in indices]
        self.data = self.data[:, keep, :]

    def tiempo_frecuencia_Epoc(self):
        """
        Calcula FFT simple de épocas.

        Returns
        -------
        np.ndarray  #Transformada de Fourier.
        """
        return np.abs(np.fft.fft(self.data, axis=-1))

    def graficar_tiempo_frecuencia_Epoc(self):
        """
        Grafica representación espectral.
        """
        espectro = self.tiempo_frecuencia_Epoc()
        plt.imshow(espectro[0, 0].reshape(1, -1), aspect='auto', cmap='viridis')
        plt.title("Tiempo-Frecuencia")
        plt.xlabel("Frecuencia")
        plt.colorbar()
        plt.show()

    def graficar_Epocas(self):
        """
        Grafica todas las épocas.
        """
        for i, epoca in enumerate(self.data):
            plt.figure(figsize=(8, 4))
            plt.plot(epoca.T)
            plt.title(f"Época {i}")
            plt.xlabel("Muestras")
            plt.ylabel("Amplitud")
            plt.show()

    def obtener_mapeo_id_evento_Epoc(self):
        """
        Obtiene IDs únicos de eventos.

        Returns
        -------
        dict  #Diccionario de IDs.
        """
        ids = list(set([evento[1] for evento in self.eventos.eventos]))
        return {id_evento: f"Evento {id_evento}" for id_evento in ids}
    
    def cambiar_id_eventos_Epoc(self, mapeo: dict):
        """
        Cambia IDs de eventos.

        Parámetros
        ----------
        mapeo : dict  #Diccionario:{viejo_id : nuevo_id}
        """
        nuevos_eventos = []
        for muestra, id_evento in self.eventos.eventos:
            nuevo_id = mapeo.get(id_evento, id_evento)
            nuevos_eventos.append((muestra, nuevo_id))
        self.eventos.eventos = nuevos_eventos

    def __len__(self):
        """
        Cantidad de épocas.
        """
        return len(self.data)

    def __str__(self):
        """
        Representación textual.
        """
        return (f"Epocas: "f"{len(self.data)} épocas, " f"{self.data.shape[1]} canales")