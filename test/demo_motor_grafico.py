#Demostración de MotorGráfico
import numpy as np

from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones
from src.biosignals.signals.ECGSignal import ECGSignal
from src.biosignals.signals.EMGSignal import EMGSignal
from src.biosignals.signals.EEGsignal import EEGSignal
from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor
from src.biosignals.preprocesamiento.ExtraerCaracteristicas import ExtraerCaracteristicas
from src.biosignals.visualización.MotorGrafico import MotorGrafico

"""
Este script demuestra el funconamiento completo de la librería utilizando señales sintéticas.
Incluye:
-creación de señales
-eventos
-anotaciones
-procesamiento
-extracción de características
-segmentación en épocas
-visualizacion
"""
"""
Parámetros generales
"""
#frecuencia de muestreo
fs = 250 #Hz
#duración de la señal
duracion = 10 #segundos
#número total de muestras
n_samples = fs*duracion
#vector temporal
times = np.arange(n_samples)/fs

"""
Creación de metada (Info)
"""
#información general de la adqusisción
info = Info(frecuencia_muestreo=fs, nombre_canales=["C3","C4","Pz"], tipos_canales=["EEG","EEG","EEG"], bad_channels=[],duracion=duracion)

"""
Creación de eventos
"""
#eventos sintéticos (muestra, id_evento)
eventos = Eventos(eventos=[(500,1),(1000,2),(1500,1)], 
                  #diccionario de mapeo
                  mapeo={1:"Estimuo A",
                         2:"Estimulo B"})

"""
Creación de anotaciones
"""
anotaciones = Anotaciones(onset=[2.0, 5.0], duration=[0.5, 1.0], description=["Artefacto", "Parpadeo"])
#generamos señales sinusoidales, simulando actividad EEG en distintas bandas
eeg_data = np.array([np.sin(2*np.pi*10*times),np.sin(2*np.pi*12*times), np.sin(2*np.pi*8*times)])
#creamos el objeto EEGSignal
eeg = EEGSignal(info = info, eventos=eventos,anotaciones=anotaciones, data=eeg_data, first_samp = 0, times = times)
#mostramos información general
print("\n ===EEF Signal===")
print(eeg)
print("\n===Eventos===")
print(eventos)
print("\n===Anotaciones===")
print(anotaciones)

"""
Preprocesamiento
"""
print("\n===Signal Processing===")
#creamos el procesador
processor = SignalProcessor(eeg)
#aplicamos filtros pasabajos
eeg_low = processor.apply_lowpass(ventana=20)
#aplicamos filtro pasaaltos
eeg_high = processor.apply_highpass(ventana=20)
#aplicamos notch de 50 Hz
eeg_notch = processor.apply_notch(freq=50)
print("Filtros aplicados correctamente")

"""
Extracción de características
"""
print("\n===Extracción de Características")
extractor = ExtraerCaracteristicas(eeg)
#media por canal
print("\nMedia: ")
print(extractor.mean())
#desviación estándar
print("\nDesviación estándar:")
print(extractor.std())
#Estadísticas específicas EEG
print("\nDescripción EEG:")
print(eeg.describe_eeg())

"""
Ssegmentación en Épocas
"""
#segmentamos usando únicamente eventos tipo 1
epocas = eeg.get_epochs(id_eventos=[1],tmin=-0.2,tmax=0.8)
#mostramos dimensiones 
print("Shape de épocas")
print(epocas.data.shape)

"""
Visualizaciones EEG
"""
#transformada de Fourier
eeg.plot_fft()
#transformada de Hilbert
eeg.plot_hilbert()
#espectrograma de un canal específico
eeg.plot_spectrogram("C3")

"""
Demostración del motor gráfico
"""
print("\n=== Motor Gráfico: Visualización Multicanal ===")
#instanciamos el motor con la señal EEG completa (3 canales)
#le ponemos un rango de tiempo de 0 a 3 segundos para que se vea claro el zoom temporal
motor_eeg = MotorGrafico(
    senal_actual=eeg,
    epocas=None,
    modo_visualizacion="señal",
    canales_visibles=None,
    mostrar_anotaciones=True,
    rango_tiempo=(0, 3.0) 
)
motor_eeg.graficar_por_renglones()

print("\n=== Motor Gráfico: Visualización de Épocas ===")
#cambiamos el motor para que ahora grafique las épocas que se segmentaron anteriormente
motor_epocas = MotorGrafico(
    senal_actual=eeg,
    epocas=epocas,
    modo_visualizacion="epocas",
    canales_visibles=None,
    mostrar_anotaciones=False,
    rango_tiempo=None
)

#graficamos todas las épocas lado a lado
motor_epocas.graficar_epocas()

#graficamos el espectrograma (tiempo-frecuencia) independiente de cada época
motor_epocas.graficar_tiempo_frecuencia_epocas()

"""
Creación de EMG Sintético
"""
print("\n===EMG Signal===")
#simulación de señal EMG con ruido
emg_data = np.array([np.random.randn(n_samples)*0.2])
#metadata EMG
emg_info = Info(frecuencia_muestreo=fs, nombre_canales=["EMG1"], tipos_canales=["EMG"], bad_channels=[], duracion=duracion)
#creamos objetos EMGSignal
emg = EMGSignal(info=emg_info,eventos=eventos,anotaciones=anotaciones, data=emg_data,first_samp=0)
print(emg)

"""
Análisis EMG
"""
#rms
print("RMS:")
print(emg.calcular_rms())
#envolvente
emg.calcular_envolvente()
#visualización envolvente
emg.plot_envolvente()

"""
Creación de ECG Sintético
"""
print("\n=== ECG Signal ===")
#simulación de ECG sintético con morfología P-QRS-T
ecg_signal = np.zeros_like(times)
for beat in np.arange(0.5, duracion, 1.0):
    # Onda P
    ecg_signal += 0.15 * np.exp(-((times - (beat - 0.2))**2) / (2 * 0.015**2))
    # Onda Q
    ecg_signal += -0.2 * np.exp(-((times - (beat - 0.04))**2) / (2 * 0.008**2))
    # Onda R
    ecg_signal += 1.2 * np.exp(-((times - beat)**2) / (2 * 0.01**2))
    # Onda S
    ecg_signal += -0.25 * np.exp(-((times - (beat + 0.03))**2) / (2 * 0.008**2))
    # Onda T
    ecg_signal += 0.35 * np.exp(-((times - (beat + 0.25))**2) / (2 * 0.04**2))
ecg_data = np.array([ecg_signal])
#metadata ECG
ecg_info = Info(frecuencia_muestreo=fs,nombre_canales=["ECG1"],tipos_canales=["ECG"], bad_channels=[], duracion = duracion)
#creamos objeto ECGSignal
ecg = ECGSignal(info=ecg_info,eventos=eventos,anotaciones=anotaciones,data=ecg_data,first_samp=0)
print(ecg)

"""
Análisis ECG
"""
print("\n=== Análisis ECG ===")

#graficamos ECG
ecg.plot_ecg()
#detectamos picos R
picos = ecg.detectar_picos(umbral=1.0)
print("Picos detectados:")
print(picos)
#graficamos ECG con picos
ecg.plot_picos()
#calculamos intervalos RR
rr = ecg.calcular_intervalos_rr()
print("Intervalos RR:")
print(rr)
#calculamos frecuencia cardíaca
fc = ecg.calcular_freq_cardiaca()
print(f"Frecuencia cardíaca: {fc:.2f} bpm")
#detectamos arritmias
arritmias = ecg.detectar_arritmias()
print("Posibles arritmias:")
print(arritmias)
#resumen
ecg.resumen_ecg()
#===FIN DEMO===
print("\nDemo ejecutada correctamente")
