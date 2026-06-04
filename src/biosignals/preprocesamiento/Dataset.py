
from src.biosignals.signals.RawSignal import RawSignal

class Dataset:

    """
    Representa un conjunto de señales biomédicas.La clase permite almacenar múltiples objetos RawSignal o clases derivadas.

    Puede utilizarse para: análisis masivo, entrenamiento de modelos, procesamiento por lotes, almacenamiento de señales.
    """

    def __init__(self,signals=None,info=None,name: str = "",description: str = ""):

        """
        Inicializa un dataset.

        Parámetros
        ----------
        signals : list[RawSignal]  #Lista de señales biomédicas.

        info : Info  #Información general del dataset.

        name : str  #Nombre del dataset.

        description : str #Descripción del dataset.
        """

        # Si no se pasa lista, creamos lista vacía
        if signals is None:
            signals = []

        self.signals = signals

        self.info = info

        self.name = name

        self.description = description

  
    # Métodos
   
    def add_signal(self, signal: RawSignal):

        """
        Agrega una señal al dataset.

        Parámetros
        ----------
        signal : RawSignal  #Señal a agregar.
        """

        self.signals.append(signal)

    def remove_signal(self, index: int):

        """
        Elimina una señal del dataset.

        Parámetros
        ----------
        index : int  #Índice de la señal.
        """

        del self.signals[index]

    def clear(self):

        """
        Elimina todas las señales del dataset.
        """

        self.signals.clear()

    def get_signal(self, index: int):

        """
        Obtiene una señal del dataset.

        Parámetros
        ----------
        index : int  #Índice de la señal.

        Returns
        -------
        RawSignal  #Señal seleccionada.
        """

        return self.signals[index]

    def __getitem__(self, index):

        """
        Permite acceder mediante [].

        Ejemplo:
        --------
        dataset[0]
        """

        return self.signals[index]

    def __len__(self):

        """
        Devuelve cantidad de señales.
        """

        return len(self.signals)

    def summary(self):

        """
        Muestra resumen del dataset.
        """

        print("Resumen Dataset")
        print("-------------------")
        print(f"Nombre: {self.name}")
        print(f"Cantidad señales: {len(self.signals)}")
        if len(self.signals) > 0:
            print(f"Canales primera señal: "f"{self.signals[0].n_channels()}")
            print(f"Muestras primera señal: "f"{self.signals[0].n_samples()}")

    def __str__(self):
        """
        Representación textual.
        """
        return (f"Dataset: "f"{len(self.signals)} señales")