#test_emg
import pytest
import numpy as np
import matplotlib
#evita abrir ventanas gráficas
matplotlib.use("Agg")
from unittest.mock import patch
from src.biosignals.signals.EMGSignal import EMGSignal
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

#fixture
@pytest.fixture
def emg_signal():
    info = Info(
        nombre_canales=["EMG1"],
        tipos_canales=["EMG"],
        bad_channels=[],
        frecuencia_muestreo=1000,
        duracion=1,
        info_experimento="Test EMG",
        info_experimentador="Federico",
        eventos=[],
        frecuencia_linea=50,
        frecuencias_corte=[20, 450],
        frecuencias_notch=[50]
    )

    eventos = Eventos([])
    anotaciones = Anotaciones([], [], [])

    #señal EMG sintética con ruido
    data = np.random.randn(1, 1000)

    return EMGSignal(info, eventos, anotaciones, data, 0)

#tests
def test_init(emg_signal):
    assert emg_signal is not None
    assert emg_signal.n_channels() == 1
    assert emg_signal.n_samples() == 1000

def test_calcular_rms(emg_signal):
    rms = emg_signal.calcular_rms()
    assert isinstance(rms, np.ndarray)
    assert rms.shape == (1,)
    assert rms[0] > 0

def test_calcular_envolvente(emg_signal):
    envolvente = emg_signal.calcular_envolvente()
    assert isinstance(envolvente, np.ndarray)
    assert envolvente.shape == emg_signal.data.shape

def test_calcular_envolvente_error(emg_signal):
    with pytest.raises(ValueError):
        emg_signal.calcular_envolvente(ventana=0)

def test_detectar_activacion(emg_signal):
    activacion = emg_signal.detectar_activacion(umbral=0.5)
    assert isinstance(activacion, np.ndarray)
    assert activacion.shape == emg_signal.data.shape
    assert activacion.dtype == bool

def test_detectar_activacion_error(emg_signal):
    with pytest.raises(TypeError):
        emg_signal.detectar_activacion("alto")

def test_plot_envolvente_error(emg_signal):
    with pytest.raises(ValueError):
        emg_signal.plot_envolvente()

@patch("src.biosignals.signals.EMGSignal.plt.show")
def test_plot_envolvente(mock_show, emg_signal):
    emg_signal.calcular_envolvente()
    emg_signal.plot_envolvente()
    mock_show.assert_called_once()

def test_str(emg_signal):
    salida = str(emg_signal)
    assert "EMGSignal" in salida
    assert "1 canales" in salida