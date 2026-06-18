#test_ecg.py
import pytest
import numpy as np
import matplotlib
#evita abrir ventanas gráficas
matplotlib.use("Agg")
from unittest.mock import patch
from src.biosignals.signals.ECGSignal import ECGSignal
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

#fixture
@pytest.fixture
def ecg_signal():
    """
    Señal ECG sintética con picos R artificiales
    """
    fs = 250
    duracion = 4
    n_samples = fs * duracion
    #señal base
    data = np.zeros((1, n_samples))
    #picos R artificiales
    data[0, 100] = 1.2
    data[0, 300] = 1.1
    data[0, 500] = 1.3
    data[0, 700] = 1.0

    info = Info(
        nombre_canales=["ECG1"],
        tipos_canales=["ECG"],
        bad_channels=[],
        frecuencia_muestreo=fs,
        duracion=duracion,
        info_experimento="Test ECG",
        info_experimentador="Federico",
        eventos=[],
        frecuencia_linea=50,
        frecuencias_corte=[0.5, 40],
        frecuencias_notch=[50]
    )

    eventos = Eventos([])
    anotaciones = Anotaciones([], [], [])
    return ECGSignal(info=info,eventos=eventos,anotaciones=anotaciones,data=data,first_samp=0)

#tests

def test_init_ecg(ecg_signal):
    print("\nProbando inicialización ECGSignal")
    assert ecg_signal.freq_cardiaca is None
    assert ecg_signal.intervalos_rr is None
    assert ecg_signal.picos is None
    assert ecg_signal.arritmias is None
    assert ecg_signal.data.shape == (1, 1000)

def test_detectar_picos(ecg_signal):
    print("\nProbando detección de picos")
    picos = ecg_signal.detectar_picos(umbral=0.9)
    assert len(picos) == 4
    assert np.array_equal(picos, np.array([100, 300, 500, 700]))

def test_calcular_intervalos_rr(ecg_signal):
    print("\nProbando cálculo de intervalos RR")
    ecg_signal.detectar_picos(0.9)
    rr = ecg_signal.calcular_intervalos_rr()
    esperado = np.array([0.8, 0.8, 0.8])
    assert np.allclose(rr, esperado)

def test_calcular_freq_cardiaca(ecg_signal):
    print("\nProbando frecuencia cardíaca")
    ecg_signal.detectar_picos(0.9)
    ecg_signal.calcular_intervalos_rr()
    fc = ecg_signal.calcular_freq_cardiaca()
    assert fc == pytest.approx(75.0)

def test_detectar_arritmias(ecg_signal):
    print("\nProbando detección de arritmias")
    ecg_signal.detectar_picos(0.9)
    ecg_signal.calcular_intervalos_rr()
    arritmias = ecg_signal.detectar_arritmias()
    #como todos los RR son 0.8 (normales), no debería haber
    assert len(arritmias) == 0

@patch("src.biosignals.signals.ECGSignal.plt.show")
def test_plot_ecg(mock_show, ecg_signal):
    """Verifica que plot_ecg intente renderizar la señal correctamente."""
    ecg_signal.plot_ecg()
    mock_show.assert_called_once()

@patch("src.biosignals.signals.ECGSignal.plt.show")
def test_plot_picos(mock_show, ecg_signal):
    """Verifica que plot_picos renderice correctamente tras detectar picos."""
    ecg_signal.detectar_picos(umbral=0.9)
    ecg_signal.plot_picos()
    mock_show.assert_called_once()

#test de errores
def test_error_rr_sin_picos(ecg_signal):
    print("\nProbando error RR sin picos")
    with pytest.raises(ValueError):
        ecg_signal.calcular_intervalos_rr()

def test_error_freq_sin_rr(ecg_signal):
    print("\nProbando error frecuencia sin RR")
    with pytest.raises(ValueError):
        ecg_signal.calcular_freq_cardiaca()

def test_error_arritmias_sin_rr(ecg_signal):
    print("\nProbando error arritmias sin RR")
    with pytest.raises(ValueError):
        ecg_signal.detectar_arritmias()

def test_error_plot_picos_sin_detectar(ecg_signal):
    print("\nProbando error plot sin picos")
    with pytest.raises(ValueError):
        ecg_signal.plot_picos()

def test_str_ecg(ecg_signal):
    print("\nProbando __str__")
    salida = str(ecg_signal)
    assert "ECGSignal" in salida