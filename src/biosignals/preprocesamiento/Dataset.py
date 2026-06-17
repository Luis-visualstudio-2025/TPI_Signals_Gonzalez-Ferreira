import os
import numpy as np
from typing import List, Optional, Any, Dict

try:
    from src.biosignals.signals.RawSignal import RawSignal
except ImportError:
    # Fallback para evitar errores en pruebas aisladas
    class RawSignal:
        pass

class Dataset:

    """
    Representa un conjunto de señales biomédicas.La clase permite almacenar múltiples objetos RawSignal o clases derivadas.

    Puede utilizarse para: análisis masivo, entrenamiento de modelos, procesamiento por lotes, almacenamiento de señales.
    """

    def __init__(self, signals: Optional[List[RawSignal]] = None, info: Optional[Any] = None, name: str = "", description: str = "") -> None:
        """
        Inicializa un dataset con validación estricta de tipos.
        Parámetros
        ----------
        signals : list[RawSignal]  #Lista de señales biomédicas.

        info : Info  #Información general del dataset.

        name : str  #Nombre del dataset.

        description : str #Descripción del dataset.
        """

        # # Si no se pasa lista, creamos lista vacía
        # if signals is None:
        #     signals = []

        # Usamos los setters para inicializar y validar de entrada
        self.signals = signals if signals is not None else []
        self.info = info
        self.name = name
        self.description = description
    
    # Encapsulamiento (Properties y Setters)
    
    @property                   # Propiedad para el nombre del dataset, permite obtener y establecer el nombre con validación de tipo.
    def name(self) -> str:
        return self._name

    @name.setter                # Setter para el nombre del dataset, valida que el valor sea una cadena de texto (str) antes de asignarlo al atributo privado _name. Si el valor no es una cadena, se lanza un error de tipo (TypeError).
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("El nombre del dataset debe ser una cadena de texto (str).")
        self._name = value

    @property                   # Propiedad para la descripción del dataset, permite obtener y establecer la descripción con validación de tipo.
    def description(self) -> str:
        return self._description

    @description.setter                # Setter para la descripción del dataset, valida que el valor sea una cadena de texto (str) antes de asignarlo al atributo privado _description. Si el valor no es una cadena, se lanza un error de tipo (TypeError).
    def description(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("La descripción debe ser una cadena de texto (str).")
        self._description = value

    @property                           # Propiedad para las señales del dataset, permite obtener y establecer la lista de señales con validación de tipo.
    def signals(self) -> List[RawSignal]:
        return self._signals

    @signals.setter                 # Setter para las señales del dataset, valida que el valor sea una lista de objetos RawSignal antes de asignarlo al atributo privado _signals. Si el valor no es una lista o si alguno de los elementos de la lista no es una instancia de RawSignal, se lanza un error de tipo (TypeError).
    def signals(self, value: List[RawSignal]) -> None:
        if not isinstance(value, list):
            raise TypeError("signals debe ser una lista de objetos RawSignal.")
        # Verificamos que todos los elementos internos sean realmente instancias de RawSignal
        for sig in value:
            if not isinstance(sig, RawSignal):
                raise TypeError("Todos los elementos de la lista deben ser instancias de RawSignal.")
        self._signals = value

    @property               # Propiedad para la información del dataset, permite obtener y establecer la información con validación de tipo.
    def info(self) -> Any:
        return self._info

    @info.setter            
    def info(self, value: Any) -> None:
        # Aquí idealmente haríamos isinstance(value, Info), pero usamos Any para desacoplar
        self._info = value
    
## Metodo para cargar señales desde archivos .txt, .csv, .npy 
    @staticmethod
    def carga_de_señal(ruta_archivo: str) -> Dict[str, Any]:
        """
        Lee un archivo físico de señal (.txt, .csv, .npy) y extrae sus datos numéricos 
        junto con metadatos básicos. Retorna un diccionario consumible por Info o RawSignal.
        """
        if not isinstance(ruta_archivo, str):
            raise TypeError("La ruta del archivo debe ser un string.")
        
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se pudo localizar el archivo en: {ruta_archivo}")

        # Extraemos la extensión en minúsculas
        _, extension = os.path.splitext(ruta_archivo)
        extension = extension.lower()

        try:
            # Carga dependiendo del formato
            if extension == '.npy':
                datos = np.load(ruta_archivo)
            elif extension == '.csv':
                # delimiter=',' es estándar para CSV
                datos = np.loadtxt(ruta_archivo, delimiter=',')
            elif extension == '.txt':
                # loadtxt asume espacios/tabulaciones por defecto
                datos = np.loadtxt(ruta_archivo)
            else:
                raise ValueError(f"Formato no soportado ('{extension}'). Use .npy, .csv o .txt.")

            # Estandarización de dimensiones a 2D (Canales x Muestras)
            if datos.ndim == 1:
                # Si es un array plano, asumimos que es 1 solo canal
                datos = datos.reshape(1, -1)
            elif datos.ndim > 2:
                raise ValueError("El archivo contiene matrices de más de 2 dimensiones, formato inválido para señales.")

            n_canales, n_muestras = datos.shape

            # Armamos el diccionario de respuesta (compatible con la clase Info previa)
            return {
                "datos_crudos": datos,               # La matriz numérica de Numpy
                "ch_names": [f"CH_{i+1}" for i in range(n_canales)],
                "sfreq": 250.0,                      # Frecuencia simulada/default si el archivo puro no la incluye
                "n_channels": n_canales,
                "duracion": float(n_muestras / 250.0) 
            }

        except Exception as e:
            raise RuntimeError(f"Ocurrió un error al intentar decodificar el archivo '{ruta_archivo}': {str(e)}") 

    # Métodos
   
    def add_signal(self, signal: RawSignal) -> None:
        """Agrega una señal al dataset validando su tipo."""
        "Parámetros"
        """signal : RawSignal  #Señal a agregar."""
        if not isinstance(signal, RawSignal):
            raise TypeError("El objeto a agregar debe ser una instancia de RawSignal.")
        self._signals.append(signal)

    def remove_signal(self, index: int)-> None:

        """
        Elimina una señal del dataset por su índice de forma segura.

        Parámetros
        ----------
        index : int  #Índice de la señal a eliminar.

        """
        if not isinstance(index, int):
            raise TypeError("El índice debe ser un número entero.")
        if index < 0 or index >= len(self._signals):
            raise IndexError(f"Índice {index} fuera de rango. El dataset tiene {len(self._signals)} señales.")
        del self.signals[index]

    def clear(self) -> None:

        """
        Elimina todas las señales del dataset.
        """
        self._signals.clear()

    def get_signal(self, index: int)-> RawSignal:

        """
        Obtiene una señal del dataset especifica controlando errores de índice.

        Parámetros
        ----------
        index : int  #Índice de la señal.

        Returns
        -------
        RawSignal  #Señal seleccionada.
        """
        if not isinstance(index, int):
            raise TypeError("El índice debe ser un número entero.")
        if index < 0 or index >= len(self._signals):
            raise IndexError("Índice fuera de rango de las señales disponibles.")
        return self._signals[index]

    def __getitem__(self, index) -> RawSignal:

        """
        Permite acceder mediante [].

        Ejemplo:
        --------
        dataset[0]
        """

        return self.get_signal[index]

    def __len__(self) -> int:

        """
        Devuelve cantidad de señales.
        """

        return len(self._signals)
    
    def __str__(self) -> str:
        """
        Representación textual.
        """
        return f"<Dataset '{self.name}' | {len(self._signals)} señales almacenadas>"

    def summary(self) -> None:

        """
        Muestra resumen limpio y estructurado del dataset por la consola.
        """

        print("===============================")
        print("       Resumen Dataset         ")
        print("===============================")
        print(f"Nombre      : {self.name if self.name else 'Sin nombre'}")
        print(f"Descripción : {self.description if self.description else 'N/A'}")
        print(f"Señales     : {len(self._signals)}")
        
        if len(self._signals) > 0 and hasattr(self._signals[0], 'n_channels'):
            try:
                # Comprobamos de manera segura si la señal tiene estos métodos antes de llamarlos
                print(f"Canales (Sig 0)  : {self._signals[0].n_channels()}")
                print(f"Muestras (Sig 0) : {self._signals[0].n_samples()}")
            except Exception:
                pass
        print("===============================")
        