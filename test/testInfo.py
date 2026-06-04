#Testeo de la clase Info

from src.biosignals.info.Info import Info

"""
Definimos una función de prueba para la clase Info:
"""
def testInfo():
    info = Info(nombre_canales = ["C1","C2"], tipos_canales= ["ECG","EMG"], bad_channels= [], frecuencia_muestreo = 1000, duracion = 10, info_experimento = "Test de la clase Info", info_experimentador = "Federico", eventos = [], frecuencia_linea = 50, frecuencias_corte = [1, 40], frecuencias_notch = [50])    
    print(info.info_experimento)
    print(f"El testeo fue realizado por: {info.info_experimentador}")
    print(f"Tenemos {info.n_channels()} canales")
    print(f"Tenemos {info.n_samples()} muestras")
    print(f"La frecuecnia de muestreo es: {info.frecuencia_muestreo} Hz")
    print(f"Las frecuecnias de corte son: {info.frecuencias_corte} Hz")
    print(f"La frecuecnia de linea es: {info.frecuencia_linea} Hz")
    print(f"La frecuencia del notch es : {info.frecuencias_notch} Hz")
#Capaz le agrego algo de texto en los print porque están medios pelados, con f"...
testInfo()
#Revisar el info.n_channels e info.n_samples
