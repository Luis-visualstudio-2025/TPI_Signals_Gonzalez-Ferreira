#Demostración de MotorGráfico
import numpy as np

from src.biosignals.visualización.MotorGrafico import MotorGrafico
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones


# =====================================================
# GENERADORES DE SEÑALES BIOMÉDICAS SIMULADAS
# =====================================================

def generar_ecg(fs=1000, duracion=5):

    t = np.linspace(0, duracion, fs * duracion)

    señal = (
        np.sin(2*np.pi*1.2*t)
        + 0.1*np.sin(2*np.pi*20*t)
        + 0.05*np.random.randn(len(t))
    )

    return señal.reshape(1, -1)


def generar_emg(n_canales=3, fs=1000, duracion=5):

    muestras = fs * duracion

    data = []

    for _ in range(n_canales):

        ruido = np.random.randn(muestras)

        envolvente = np.abs(
            np.sin(
                np.linspace(0, 6*np.pi, muestras)
            )
        )

        canal = ruido * envolvente

        data.append(canal)

    return np.array(data)


def generar_eeg(n_canales=8, fs=1000, duracion=5):

    t = np.linspace(0, duracion, fs * duracion)

    data = []

    for _ in range(n_canales):

        alfa = np.sin(2*np.pi*10*t)

        beta = 0.5*np.sin(2*np.pi*20*t)

        ruido = 0.2*np.random.randn(len(t))

        canal = alfa + beta + ruido

        data.append(canal)

    return np.array(data)


# =====================================================
# CREA UN RAWSIGNAL
# =====================================================

def crear_rawsignal(data, tipo_senal):

    n_canales = data.shape[0]

    info = Info(
        nombre_canales=[f"C{i}" for i in range(1, n_canales+1)],
        tipos_canales=[tipo_senal] * n_canales,
        bad_channels=[],
        frecuencia_muestreo=1000,
        duracion=data.shape[1] / 1000,
        info_experimento=f"Demo {tipo_senal}",
        info_experimentador="Federico",
        eventos=[],
        frecuencia_linea=50,
        frecuencias_corte=[1, 40],
        frecuencias_notch=[50]
    )

    eventos = Eventos([
        (1000, "Inicio"),
        (2500, "Estímulo"),
        (4000, "Fin")
    ])

    anotaciones = Anotaciones([], [], [])

    return RawSignal(
        info,
        eventos,
        anotaciones,
        data,
        0
    )


# =====================================================
# FUNCIÓN DE DEMOSTRACIÓN
# =====================================================

def mostrar_senal(rawsignal, titulo):

    print("\n===================================")
    print(titulo)
    print("===================================")

    print("Canales:", rawsignal.info.n_channels())
    print("Muestras:", rawsignal.info.n_samples())

    motor = MotorGrafico(
        senal_actual=rawsignal,
        epocas=None,
        modo_visualizacion="señal",
        canales_visibles=None,
        mostrar_anotaciones=True,
        rango_tiempo=None
    )

    motor.graficar_senal()


# =====================================================
# DEMOSTRACIONES
# =====================================================

if __name__ == "__main__":

    # ECG MONOCANAL
    ecg = generar_ecg()

    raw_ecg = crear_rawsignal(
        ecg,
        "ECG"
    )

    mostrar_senal(
        raw_ecg,
        "DEMO ECG MONOCANAL"
    )


    # EMG 3 CANALES
    emg = generar_emg(
        n_canales=3
    )

    raw_emg = crear_rawsignal(
        emg,
        "EMG"
    )

    mostrar_senal(
        raw_emg,
        "DEMO EMG 3 CANALES"
    )


    # EEG 8 CANALES
    eeg8 = generar_eeg(
        n_canales=8
    )

    raw_eeg8 = crear_rawsignal(
        eeg8,
        "EEG"
    )

    mostrar_senal(
        raw_eeg8,
        "DEMO EEG 8 CANALES"
    )


    # EEG 32 CANALES
    eeg32 = generar_eeg(
        n_canales=32
    )

    raw_eeg32 = crear_rawsignal(
        eeg32,
        "EEG"
    )

    mostrar_senal(
        raw_eeg32,
        "DEMO EEG 32 CANALES"
    )