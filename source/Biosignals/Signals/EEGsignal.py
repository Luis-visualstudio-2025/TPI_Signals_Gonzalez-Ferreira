#### El siguiente codigo comentado es el ejemplo de Lucas para la clase EEGSignal, 
#### se basa en la clase RawSignal y ofrece métodos específicos para señales EEG, como la transformada de Hilbert. 
#### Se importan las funciones necesarias de scipy.signal y se hereda de RawSignal para mantener la estructura común de las señales.


# from fede.signals import RawSignal
# from fede.signals import ExtractorCaracteristicas
# from scipy.signal import hilbert

# class EEGSignal(RawSignal):
#     """
#     Clase especializada para representar señales EEG.
#     Hereda de RawSignal y puede incluir métodos específicos para EEG.
#     """

#     def __init__(self, data, info):
#         super().__init__(data, info)
#         self.hilbert = None  # Atributo para almacenar la transformada de Hilbert de la señal EEG
#         #Aquí podríamos agregar atributos específicos para EEG si es necesario

#     def getHilbert(self):
#         """
#         Método para obtener la transformada de Hilbert de la señal EEG.
#         Retorna la señal transformada utilizando la función hilbert de scipy.
#         """
#         self.hilbert = hilbert(self.data, axis=1)
#         return self.hilbert
    

# eeg = EEG()
# _ = eeg.getHilbert()
# eeg.

