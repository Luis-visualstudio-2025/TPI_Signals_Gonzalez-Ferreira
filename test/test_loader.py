import pytest
import numpy as np
import os
from src.biosignals.io.loader import load_signal # Asegúrate de ajustar este import
from src.biosignals.signals.ECGSignal import ECGSignal
from src.biosignals.signals.RawSignal import RawSignal

# Fixture para crear un archivo temporal automáticamente
@pytest.fixture
def temp_csv_file(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    file_path = d / "test_signal.csv"
    # Creamos una señal de prueba: 2 canales, 100 muestras
    data = np.random.randn(2, 100)
    np.savetxt(file_path, data, delimiter=',')
    return str(file_path)

def test_load_signal_basic(temp_csv_file):
    """Prueba la carga básica con RawSignal."""
    senal = load_signal(temp_csv_file, fs=500.0)
    
    assert isinstance(senal, RawSignal)
    assert senal.n_channels() == 2
    assert senal.info.frecuencia_muestreo == 500.0
    assert senal.n_samples() == 100

def test_load_signal_ecg_custom_metadata(temp_csv_file):
    """Prueba que el loader detecta correctamente la clase ECG y usa los defaults."""
    senal = load_signal(
        temp_csv_file, 
        signal_class=ECGSignal, 
        info_experimentador="Dr. Test"
    )
    
    assert isinstance(senal, ECGSignal)
    assert senal.info.tipos_canales[0] == 'ecg'
    assert senal.info.info_experimentador == "Dr. Test"
    # Verifica que haya aplicado los defaults de ECG
    assert senal.info.frecuencias_corte == [0.05, 150.0]

def test_load_signal_con_anotaciones_dict(temp_csv_file):
    """Prueba la carga pasando anotaciones como un diccionario."""
    anotaciones_data = {
        'onset': [10.0, 50.0],
        'duration': [1.0, 2.0],
        'description': ['pico', 'ruido']
    }
    
    senal = load_signal(temp_csv_file, anotaciones=anotaciones_data)
    
    assert len(senal.anotaciones.onset) == 2
    assert senal.anotaciones.description[0] == 'pico'

def test_load_file_not_found():
    """Prueba que lance error si el archivo no existe."""
    with pytest.raises(FileNotFoundError):
        load_signal("archivo_que_no_existe.csv")

def test_load_invalid_format():
    """Prueba que lance error con extensiones no soportadas."""
    with open("test.mp3", "w") as f: f.write("dummy")
    with pytest.raises(ValueError, match="no soportado"):
        load_signal("test.mp3")
    os.remove("test.mp3")