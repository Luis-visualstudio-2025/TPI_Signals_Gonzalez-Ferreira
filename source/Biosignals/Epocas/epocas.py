class Epocas:
    def __init__(self, signal, eventos, id_eventos=None, tmin=-0.2, tmax=0.5, picks=None, reject=None):
        self.signal = signal
        self.eventos = eventos
        self.id_eventos = id_eventos
        self.tmin = tmin
        self.tmax = tmax
        self.picks = picks
        self.reject = reject
   
    def promedio_Epoc(self):
        # Implementar el método para computar el promedio sobre todas las épocas
        pass
    def recortar_Epoc(self, tmin, tmax):
        # Implementar el método para recortar un intervalo de tiempo de las épocas
        pass
    def tiempo_frecuencia_Epoc(self):
        # Implementar el método para computar la representación en tiempo-frecuencia de las épocas
        pass    
    def graficar_tiempo_frecuencia_Epoc(self):
        # Implementar el método para generar una gráfica de tiempo-frecuencia para una o más épocas
        pass
    def eliminar_canales_Epoc(self, canales):
        # Implementar el método para eliminar canales de las épocas
        pass
    def get_data_Epoc(self):
        # Implementar el método para obtener las muestras de cada época
        pass
    def graficar_Epocas(self):
        # Implementar el método para graficar las épocas una al lado de la otra
        pass
    def obtener_mapeo_id_evento_Epoc(self):
        # Implementar el método para obtener un diccionario con el mapeo del id_evento y su nombre asociado
        pass
    def cambiar_id_eventos_Epoc(self, mapeo):
        # Implementar el método para cambiar el valor de los id_eventos
        pass