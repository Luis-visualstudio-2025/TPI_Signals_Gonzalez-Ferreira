import pandas as pd
from collections import Counter

class Anotaciones:
    """
    Representa anotaciones asociadas a una señal biomédica.
    Cada anotación contiene: tiempo de inicio, duración y descripción.
    Opcionalmente puede incluir tiempo inicial de referencia (t0) y nombres de canales asociados.
    La clase permite agregar, aliminar y buscar anotaciones, así como expoprtar e importar CSV.
    """
    def __init__(self, onset, duration, description, t0=None, ch_names=None):

        """
        Inicializa un objeto Anotaciones.
        
        Parámetros
        ----------
        onset : list  #Lista de tiempos de inicio
        duration : list  #Lista de duraciones
        description : list  #Lista de descripciones
        t0 : float | None  #Tiempo inicial de referencia
        ch_names : list | None  #Lista de canales asociados"""

        #Contratos
        #Todas las listas deben de tener la misma longitud
        if not (len(onset)==len(duration)==len(description)):
            raise ValueError("Las lsitas de onset, duration y description deben tener la misma longitud")
        
        for o, d, desc in zip(onset, duration, description):
            if o < 0:
                raise ValueError("onset no puede ser negativo")
            if d < 0: 
                raise ValueError("duration no puede ser negativo")
            if not isinstance(desc, str):
                raise TypeError("description debe ser un string")
        #Atributos
        #Tiempo de cada anotación
        self.onset = onset
        #Duración de cada anotación
        self.duration = duration
        #Descripción textual de cada anotación
        self.description = description
        #Tiempo inicial de referencia
        self.t0 = t0
        #Canales asociados
        self.ch_names = ch_names

    #Métodos
    def __iter__(self):
        """
        Permite iterar sobre las anotaciones.
        
        Returns
        -------
        iterator  #Un iterador con onset, duration y description
        """
        return iter(zip(self.onset, self.duration, self.description))
    def __len__(self):
        """
        Devuelve la cantidad de anotaciones
        Returns
        -------
        int  #Número de anotaciones"""
        return len(self.onset)
    def __str__(self):
        """
        Representación textual del objeto.
        Returns
        -------
        str  #Resumen de anotaciones
        """

        #Contamos cantidad por descripción
        conteo_descripciones = Counter(self.description)
        return f"Anotaciones: {len(self.onset)} anotaciones, Tipos: {dict(conteo_descripciones)}"
    def add(self, onset, duration, description):
        """
        Agrega una nueva anotación.
        
        Parámetros
        ----------
        onset : float  #Tiempo de inicio
        duration : float  #Duración
        description : str  #Descripción de la anotación
        """
        if onset < 0:
            raise ValueError("onset no puede ser negativo")
        if duration < 0:
            raise ValueError("duration no puede ser negativa")
        if not isinstance(description, str):
            raise TypeError("description debe ser string")
        self.onset.append(onset)
        self.duration.append(duration)
        self.description.append(description)

    def remove(self, index):
        """
        Elimina una anotación según su índice.
        Parámetros
        ----------
        index : int  #índice de la anotación
        """
        if index < 0 or index >= len(self.onset):
            raise IndexError("índice fuera de rango")
        del self.onset[index]
        del self.duration[index]
        del self.description[index]

    def get_annotations(self):
        """
        Devuelve las anotaciones en formato DataFrame.
        Returns
        -------
        pd.DataFrame  #Tabla con anotaciones.
        """
        return pd.DataFrame({'onset': self.onset,'duration': self.duration,'description': self.description})
    
    def find(self, description):
        """
        Busca anotaciones por descripción.
        Parámetros
        ----------
        description : str  #Descripción a buscar
        Returns
        -------
        pd.DataFrame  #Anotaciones encontrada.
        """
        df = self.get_annotations()
        return df[df['description'] == description]
    def save(self, filename):
        """
        Guarda anotaciones en un archivo CSV.
        Parámetros
        ----------
        filname : str  #Nombre del archivo CSV.
        """
        df = self.get_annotations()
        df["t0"] = self.t0
        df["ch_names"] = [self.ch_names]*len(df)
        df.to_csv(filename, index=False)
    
    @classmethod
    def load(cls, filename):
        """
        Cargamos anotaciones desde un archivo .csv, .txt o .json.
        Parámetros
        ----------
        filename : str  #Ruta del archivo .csv, .txt o .json.
        """
        #Leemos el .CSV, .txt o .json
        if filename.endswith('.csv'):                       #Si es un archivo CSV, lo leemos con pandas
            df = pd.read_csv(filename)                      
        elif filename.endswith('.txt'):                     #Si es un archivo de texto, lo leemos con pandas usando tabulaciones como delimitadores
            df = pd.read_csv(filename, delimiter='\t')
        elif filename.endswith('.json'):                    ##Si es un archivo JSON, lo leemos con pandas usando el formato de registros
            df = pd.read_json(filename, orient='records')
        else:
            raise ValueError("Formato no soportado. Use .csv, .txt o .json")

        #Recuperamos columnas
        onset = df['onset'].tolist()
        duration = df['duration'].tolist()
        description = df['description'].tolist()
        #Recuperamos atributos opocionales
        t0 = df['t0'].iloc[0] if 't0' in df.columns else None
        ch_names = df['ch_names'].iloc[0] if 'ch_names' in df.columns else None
        #creamos y devolvemos nueva instancia
        return cls(onset=onset, duration=duration, description=description, t0=t0, ch_names=ch_names)
