#Clase Info
from typing import List, Optional

class Info:
    """
    Clase para almacenar metadata de una señal biomédica.
    Contiene información sobre canales, frecuencia de muestreo,
    duración, filtros aplicados y datos experimentales.
    """
    def __init__(
        self,
        frecuencia_muestreo: float,
        nombre_canales: List[str],
        tipos_canales: List[str],
        bad_channels: Optional[List[str]] = None,
        duracion: Optional[float] = None,
        info_experimento: Optional[str] = None,
        info_experimentador: Optional[str] = None,
        eventos=None,
        frecuencia_linea: Optional[float] = 50,
        frecuencias_corte: Optional[List[float]] = None,
        frecuencias_notch: Optional[List[float]] = None
    ):
        """
        Inicializa un objeto Info.

        Parámetros
        ----------
        frecuencia_muestreo : float
            Frecuencia de muestreo de la señal.

        nombre_canales : list[str]
            Lista con nombres de canales.

        tipos_canales : list[str]
            Lista con tipos de canales.

        bad_channels : list[str], opcional
            Lista de canales defectuosos.

        duracion : float, opcional
            Duración total de la señal.

        info_experimento : str, opcional
            Información sobre el experimento.

        info_experimentador : str, opcional
            Información del experimentador.

        eventos : Eventos, opcional
            Eventos asociados a la señal.

        frecuencia_linea : float, opcional
            Frecuencia de línea eléctrica (default 50 Hz).

        frecuencias_corte : list[float], opcional
            Frecuencias de corte de filtros.

        frecuencias_notch : list[float], opcional
            Frecuencias de filtros notch.
        """

        #contratos mínimos
        if frecuencia_muestreo <= 0:
            raise ValueError("La frecuencia de muestreo debe ser positiva.")

        if len(nombre_canales) != len(tipos_canales):
            raise ValueError("nombre_canales y tipos_canales deben tener la misma longitud.")
        #asignación de atributos
        self.frecuencia_muestreo = frecuencia_muestreo
        self.nombre_canales = nombre_canales
        self.tipos_canales = tipos_canales
        self.bad_channels = bad_channels if bad_channels is not None else []
        self.duracion = duracion
        self.info_experimento = info_experimento
        self.info_experimentador = info_experimentador
        self.eventos = eventos
        self.frecuencia_linea = frecuencia_linea
        self.frecuencias_corte = (frecuencias_corte if frecuencias_corte is not None else [])
        self.frecuencias_notch = (frecuencias_notch if frecuencias_notch is not None else [])

    #métodos
    def __contains__(self, item):
        """
        Permite verificar si un canal existe.
        Ejemplo:
        --------
        "C3" in info
        """
        return item in self.nombre_canales

    def __getitem__(self, key):
        """
        Permite acceder a atributos como diccionario.
        Ejemplo:
        --------
        info["nombre_canales"]
        """
        return getattr(self, key)

    def __len__(self):
        """
        Retorna la cantidad de canales.
        """
        return len(self.nombre_canales)

    def __str__(self):
        """
        Representación textual del objeto.
        """
        return (
            f"Info: {len(self.nombre_canales)} canales, "
            f"fs={self.frecuencia_muestreo} Hz, "
            f"duración={self.duracion if self.duracion else 'No definida'} s")

    #métodos tipo diccionario
    def get(self, key):
        """
        Obtiene un atributo por nombre.
        """
        return getattr(self, key)

    def keys(self):
        """
        Retorna las claves disponibles.
        """
        return vars(self).keys()

    def items(self):
        """
        Retorna pares clave-valor.
        """
        return vars(self).items()

    #métodos informativos

    def n_channels(self):
        """
        Retorna cantidad de canales.
        """
        return len(self.nombre_canales)

    def n_samples(self):
        """
        Calcula número total de muestras.
        """
        if self.duracion is None:
            raise ValueError("La duración no está definida.")
        return int(self.frecuencia_muestreo * self.duracion)

    def frec_muestreo(self):
        """
        Retorna frecuencia de muestreo.
        """
        return self.frecuencia_muestreo
    
    #métodos de modificación
    def rename_channels(self, new_names: List[str]):
        """
        Renombra canales.
        """
        if len(new_names) != len(self.nombre_canales):
            raise ValueError("La cantidad de nuevos nombres debe coincidir con la cantidad de canales.")
        self.nombre_canales = new_names
