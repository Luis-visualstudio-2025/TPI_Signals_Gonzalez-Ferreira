#test_eeg
import pytest
import numpy as np
import matplotlib
matplotlib.use("Agg")

from src.biosignals.signals.EEGsignal import EEGSignal
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

#fixture
@pytest.fixture
def eeg_signal():

    fs = 250
    duracion = 4
    n_samples = fs * duracion
    times = np.arange(n_samples) / fs

    info = Info(
        nombre_canales=["C3", "C4", "Pz"],
        tipos_canales=["EEG", "EEG", "EEG"],
        bad_channels=[],
        frecuencia_muestreo=fs,
        duracion=duracion,
        info_experimento="Test EEG",
        info_experimentador="Federico",
        eventos=[],
        frecuencia_linea=50,
        frecuencias_corte=[1, 40],
        frecuencias_notch=[50])

    eventos = Eventos(
        eventos=[(250, 1), (500, 2)],
        mapeo={1: "A", 2: "B"})

    anotaciones = Anotaciones([], [], [])

    data = np.array([
        np.sin(2*np.pi*10*times),
        np.sin(2*np.pi*12*times),
        np.sin(2*np.pi*8*times)])

    return EEGSignal(
        info=info,
        eventos=eventos,
        anotaciones=anotaciones,
        data=data,
        first_samp=0,
        times=times)

#tests
def test_init(eeg_signal):
    assert eeg_signal.data.shape == (3, 1000)
    assert eeg_signal.info.frecuencia_muestreo == 250
    assert eeg_signal.is_filtered is False

def test_describe_eeg(eeg_signal):
    stats = eeg_signal.describe_eeg()
    assert isinstance(stats, dict)
    assert "C3" in stats
    assert "mean" in stats["C3"]

def test_picks_channels(eeg_signal):
    nuevo = eeg_signal.picks_channels(["C3", "Pz"])
    assert nuevo.data.shape[0] == 2
    assert nuevo.info.nombre_canales == ["C3", "Pz"]

def test_picks_channels_invalido(eeg_signal):
    with pytest.raises(ValueError):
        eeg_signal.picks_channels(["X1"])

def test_crop(eeg_signal):
    recortada = eeg_signal.crop(0.5, 2.0)
    assert recortada.data.shape[1] == 375

def test_crop_invalido(eeg_signal):
    with pytest.raises(ValueError):
        eeg_signal.crop(2, 1)

def test_apply_filter(eeg_signal):
    filtrada = eeg_signal.apply_filter_eeg(l_freq=1, h_freq=40)
    assert filtrada is not None
    assert filtrada.data.shape == eeg_signal.data.shape

def test_get_epochs(eeg_signal):
    epocas = eeg_signal.get_epochs(id_eventos=[1], tmin=-0.2, tmax=0.5)
    assert epocas is not None

def test_plot_fft(eeg_signal):
    eeg_signal.plot_fft()
    assert True

def test_plot_hilbert(eeg_signal):
    eeg_signal.plot_hilbert()
    assert True

def test_plot_spectrogram(eeg_signal):
    eeg_signal.plot_spectrogram("C3")
    assert True

def test_str(eeg_signal):
    texto = str(eeg_signal)
    assert "EEGSignal" in texto