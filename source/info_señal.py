class Info_señal:                                                   # Definimos la clase info_señal para almacenar información relevante de las señales
    def __init__(self, nombre_canales, tipos_canales, bad_channels, frecuencia_muestreo, duracion, info_experimento, info_experimentador, eventos, frecuencia_linea, frecuencias_corte, frecuencias_notch):         # Constructor que recibe toda la información relevante de las señales, como nombre de canales, tipos de canales, canales malos, frecuencia de muestreo, duración, información del experimento y experimentador, eventos, frecuencia de línea, frecuencias de corte y frecuencias del filtro Notch
        self.nombre_canales = nombre_canales                        # Asignamos el valor de nombre_canales al atributo de la instancia
        self.tipos_canales = tipos_canales                          # Asignamos el valor de tipos_canales al atributo de la instancia
        self.bad_channels = bad_channels                            # Asignamos el valor de bad_channels al atributo de la instancia
        self.frecuencia_muestreo = frecuencia_muestreo              # Asignamos el valor de frecuencia_muestreo al atributo de la instancia
        self.duracion = duracion                                    # Asignamos el valor de duracion al atributo de la instancia
        self.info_experimento = info_experimento                    # Asignamos el valor de info_experimento al atributo de la instancia
        self.info_experimentador = info_experimentador              # Asignamos el valor de info_experimentador al atributo de la instancia
        self.eventos = eventos                                      # Asignamos el valor de eventos al atributo de la instancia     
        self.frecuencia_linea = frecuencia_linea                    # Asignamos el valor de frecuencia_linea al atributo de la instancia
        self.frecuencias_corte = frecuencias_corte                  # Asignamos el valor de frecuencias_corte al atributo de la instancia
        self.frecuencias_notch = frecuencias_notch                  # Asignamos el valor de frecuencias_notch al atributo de la instancia

    def __contains__(self, item):                                   # Método para verificar si un item está presente en el nombre de canales, retorna True si el item está presente y False si no lo está. En este contexto, la clave sería el nombre de un canal u otra información. Ej: çh_namesïn info
        return item in self.nombre_canales

    def __getitem__(self, key):                                     # Método para obtener el valor de un atributo específico usando la sintaxis de acceso a elementos, retorna el valor del atributo correspondiente a la clave proporcionada. En este contexto, la clave sería el nombre de un canal u otra información. Ej: info['ch_names'] para obtener el nombre de los canales
        return getattr(self, key)           

    def __len__(self):                                              # Método para obtener la cantidad de canales, retorna el número de canales presentes en la señal. En este contexto, se asume que el número de canales se determina por la longitud de la lista de nombres de canales.
        return len(self.nombre_canales)

    def __str__(self):
        return f"Info de la señal: {len(self.nombre_canales)} canales, duración: {self.duracion} segundos"   # Método para obtener una representación en forma de cadena de la información de la señal, retorna una cadena que describe la información de la señal, incluyendo el número de canales y la duración. En este contexto, se muestra el número de canales y la duración de la señal.

    def get(self, key):                                             # Método para obtener el valor de un atributo específico usando la sintaxis de acceso a elementos, retorna el valor del atributo correspondiente a la clave proporcionada. En este contexto, la clave sería el nombre de un canal u otra información. Ej: info.get('ch_names') para obtener el nombre de los canales
        return getattr(self, key)

    def keys(self):                                                 # Método para obtener las claves de los atributos de la clase, retorna una lista de las claves de los atributos presentes en la clase. En este contexto, se mostrarían las claves de los atributos relacionados con la información de la señal, como nombre de canales, tipos de canales, etc.
        return vars(self).keys()

    def items(self):                                                # Método para obtener los pares clave-valor de los atributos de la clase, retorna una lista de tuplas donde cada tupla contiene una clave y su valor correspondiente. En este contexto, se mostrarían los pares clave-valor de los atributos relacionados con la información de la señal, como nombre de canales, tipos de canales, etc.
        return vars(self).items()

    def n_channels(self):                                           # Método para obtener la cantidad de canales, retorna el número de canales presentes en la señal. En este contexto, se asume que el número de canales se determina por la longitud de la lista de nombres de canales.
        return len(self.nombre_canales)

    def n_samples(self):                                            # Método para obtener la cantidad de muestras, retorna el número total de muestras presentes en la señal. En este contexto, se calcula multiplicando la frecuencia de muestreo por la duración de la señal, lo que da como resultado el número total de muestras presentes en la señal. 
        return int(self.frecuencia_muestreo * self.duracion)

    def rename_channels(self, new_names):                           # Método para renombrar los canales, recibe una lista de nuevos nombres y actualiza el atributo de nombre de canales con los nuevos nombres proporcionados. En este contexto, se espera que la cantidad de nuevos nombres coincida con la cantidad de canales presentes en la señal, por lo que se verifica esta condición antes de actualizar el atributo. Si la cantidad de nuevos nombres no coincide con la cantidad de canales, se lanza un error.
        if len(new_names) != len(self.nombre_canales):
            raise ValueError("La cantidad de nuevos nombres debe coincidir con la cantidad de canales.")
        self.nombre_canales = new_names

class Señal:                                                        # Definimos la clase señal para representar una señal con un nombre y una frecuencia específicos
    def __init__(self, nombre, frecuencia):
        self.nombre = nombre
        self.frecuencia = frecuencia

    def __str__(self):
        return f"Señal: {self.nombre}, Frecuencia: {self.frecuencia} Hz"
    
    def __repr__(self):
        return f"Señal(nombre='{self.nombre}', frecuencia={self.frecuencia})"
    def __eq__(self, other):
        if isinstance(other, Señal):
            return self.nombre == other.nombre and self.frecuencia == other.frecuencia
        return False
    def __hash__(self):
        return hash((self.nombre, self.frecuencia))
    def __contains__(self, item):
        return item in self.nombre
    def __getitem__(self, key):
        if key == 'nombre':
            return self.nombre
        elif key == 'frecuencia':
            return self.frecuencia
        else:
            raise KeyError(f"Clave '{key}' no encontrada en la señal.")
    def __len__(self):
        return len(self.nombre)