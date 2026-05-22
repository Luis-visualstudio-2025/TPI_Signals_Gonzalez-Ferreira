#Testeo de la clase Info

from source.Biosignals.Info.Info import Info

"""
Definimos una funciónd e prueba para la clase Info:
"""
def testInfo():
    info = Info(nombre_canales = ["C1","C2"], tipos_canales= ["ECG","EMG"], bad_channels= [], frecuencia_muestreo = 1000, duracion = 10, info_experimento = "Test de la Clase Info", info_experimentador = "Federico", eventos = [], frecuencia_linea = 50, frecuencias_corte = [1, 40], frecuencias_notch = [50])    
    print(info.info_experimento)
    print(info.info_experimentador)
    print(info.n_channels())
    print(info.n_samples())
    print(info.frecuencia_muestreo)
    print(info.frecuencias_corte)
    print(info.frecuencia_linea)
    print(info.frecuencias_notch)

testInfo()
#Revisar el info.n_channels e info.n_samples
