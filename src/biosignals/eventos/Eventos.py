#Clase Eventos
import pandas as pd
from collections import Counter

class Eventos:
    """
    Representa eventos asociados a la señal.
    Cada evento se represente como una tupla (muestra, id_evento).
    """

    def __init__(self, eventos, mapeo=None):
        """
        Inicializamos un objeto Eventos.
        Parámetros
        ----------
        eventos : list  #Lista de eventos [(muestra, id_evento), ...]
        """
        #Contrato
        #Verificamos que cada evento tenga 2 elementos: muestra e id_evento
        for evento in eventos:
            if len(evento) != 2:
                raise ValueError("Cada evento debe ser una tupla (muestra, id_evento)")
        #Lista de eventos
        self.eventos = eventos
        if mapeo is None:
            mapeo = {}
        self.mapeo = mapeo
    
    #Métodos
    def __iter__(self):
        """
        Permite iterar sobre los eventos.
        Returns
        -------
        iterator  #Un iterador con eventos.
        """
        return iter(self.eventos)
    def __len__(self):
        """
        Devuelve la cantidad de eventos.
        Returns
        -------
        int  #Número de eventos.
        """
        return len(self.eventos)
    def __str__(self):
        """
        Representación textual del objeto.
        Returns
        -------
        str  #Resumen de eventos.
        """
        #Contamos cantidad de eventos por id_evento
        conteo_eventos = Counter([evento[1] for evento in self.eventos])
        return f"Eventos: {len(self.eventos)} eventos, Tipos: {dict(conteo_eventos)}"
    def add(self, muestra, id_evento):
        """
        Agrega un nuevo evento.
        Parámetros
        ----------
        muestra : int  #Número de muestra del evento.
        id_evento : int  #Identificador del evento.
        """
        self.eventos.append((muestra, id_evento))
    def remove(self, index):
        """
        Elimina un evento según índice
        Parámetros
        ----------
        index : int #Índice del evento a eliminar.
        """
        del self.eventos[index]
    def get_events(self):
        """
        Devuelve eventos como DataFrame.
        Returns
        -------
        pd.DataFrame #Tabla con eventos.
        """
        return pd.DataFrame(self.eventos, columns=['muestra', 'id_evento'])
    def find(self, id_evento):
        """
        Busca eventos por id_evento.
        Parámetros
        ----------
        id_evento : int  #Identificador del evento a buscar.
        Returns
        -------
        pd.DataFrame #Tabla con eventos encontrados.
        """
        df = self.get_events()
        return df[df['id_evento'] == id_evento]
    def save(self, filename):
        """
        Guarda eventos en un archivo CSV.
        Parámetros
        ----------
        filename : str  #Nombre del archivo CSV.
        """
        df = self.get_events()
        df.to_csv(filename, index=False)
    def load(self, filename):
        """
        Carga eventos desde un archivo CSV.
        Parámetros
        ----------
        filename : str  #Ruta del archivo CSV.
        Returns
        -------
        None
        """
        df = pd.read_csv(filename)
        self.eventos = list(zip(df['muestra'], df['id_evento']))