import pytest
import numpy as np
import os
import shutil

# Importaciones de tu arquitectura
from src.biosignals.io.loader import load_signal, _buscar_archivo_recursivo
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.signals.ECGSignal import ECGSignal
from src.biosignals.signals.EMGSignal import EMGSignal
from src.biosignals.signals.EEGsignal import EEGSignal
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

# =====================================================================
# FIXTURES: Generación de entorno controlado y archivos de prueba
# =====================================================================

@pytest.fixture
def archivos_de_prueba(tmp_path):
    """Crea múltiples archivos temporales con diferentes formatos y problemas."""
    d = tmp_path / "data"
    d.mkdir()
    
    rutas = {}
    
    # 1. Archivo vertical delimitado por comas (100 muestras, 2 canales)
    vertical_path = d / "vertical.csv"
    data_vertical = np.random.randn(100, 2)
    np.savetxt(vertical_path, data_vertical, delimiter=',')
    rutas['vertical'] = str(vertical_path)
    
    # 2. Archivo sucio con cabecera y texto al final
    sucio_path = d / "sucio.txt"
    with open(sucio_path, 'w') as f:
        f.write("Index, Channel1, Channel2, Timestamp\n")
        for i in range(10):
            f.write(f"{i}, {np.random.rand()}, {np.random.rand()}, 2026-10-10\n")
    rutas['sucio'] = str(sucio_path)
    
    # 3. Archivo Numpy puro
    npy_path = d / "binario.npy"
    np.save(npy_path, np.random.randn(4, 50))
    rutas['npy'] = str(npy_path)
    
    # 4. Archivo oculto en subcarpeta para probar recursividad
    sub_dir = d / "subcarpeta" / "profunda"
    sub_dir.mkdir(parents=True)
    oculto_path = sub_dir / "escondido.csv"
    np.savetxt(oculto_path, np.random.randn(3, 20), delimiter=',')
    rutas['oculto'] = str(oculto_path)
    
    # Guardamos el directorio base temporal para forzar la búsqueda ahí
    rutas['base_dir'] = str(d)
    
    return rutas

# =====================================================================
# TESTS
# =====================================================================

def test_auto_transposicion(archivos_de_prueba):
    """Verifica que el loader invierta la matriz si detecta formato muestras x canales."""
    # FIX: Agregamos delimiter=','
    senal = load_signal(archivos_de_prueba['vertical'], fs=250.0, delimiter=',')
    
    assert senal.n_channels() == 2
    assert senal.n_samples() == 100
    assert senal.data.shape == (2, 100)

def test_cabeceras_y_usecols(archivos_de_prueba):
    """Verifica el salto de texto y la omisión de la columna de timestamps."""
    senal = load_signal(
        archivos_de_prueba['sucio'], 
        delimiter=',', 
        usecols=(0, 1, 2)
    )
    
    assert senal.n_channels() == 3
    # FIX: Se corrigió la línea cortada (assert senal.n_)
    assert senal.n_samples() == 10 

def test_carga_archivo_numpy(archivos_de_prueba):
    """Verifica la carga de archivos binarios .npy."""
    senal = load_signal(archivos_de_prueba['npy'])
    assert senal.data.shape == (4, 50)

def test_busqueda_recursiva(archivos_de_prueba, monkeypatch):
    """Verifica que _buscar_archivo_recursivo encuentre un archivo solo por su nombre."""
    nombre_archivo = "escondido.csv"
    monkeypatch.chdir(archivos_de_prueba['base_dir'])
    
    # FIX: Le indicamos la coma porque escondido.csv lo generamos con numpy
    senal = load_signal(nombre_archivo, delimiter=',')
    assert senal.data.shape == (3, 20)

def test_metadatos_polimorficos_ecg(archivos_de_prueba):
    """Comprueba los defaults clínicos de ECG."""
    # FIX: Agregamos delimiter=','
    senal = load_signal(archivos_de_prueba['vertical'], signal_class=ECGSignal, delimiter=',')
    assert isinstance(senal, ECGSignal)
    assert senal.info.tipos_canales == ['ecg', 'ecg']
    assert senal.info.frecuencias_corte == [0.05, 150.0]

def test_metadatos_polimorficos_emg(archivos_de_prueba):
    """Comprueba los defaults clínicos de EMG."""
    # FIX: Agregamos delimiter=','
    senal = load_signal(archivos_de_prueba['vertical'], signal_class=EMGSignal, delimiter=',')
    assert isinstance(senal, EMGSignal)
    assert senal.info.tipos_canales == ['emg', 'emg']
    assert senal.info.frecuencias_corte == [10.0, 500.0]

def test_inyeccion_eventos_y_anotaciones(archivos_de_prueba):
    """Verifica que los objetos de soporte se guarden adecuadamente al pasarlos por kwargs."""
    obj_eventos = Eventos(eventos=[(10, 1), (50, 2)])
    obj_anotaciones = Anotaciones(onset=[1.0], duration=[0.5], description=["Pico"])
    
    # FIX: Agregamos delimiter=','
    senal = load_signal(
        archivos_de_prueba['vertical'], 
        delimiter=',',
        eventos=obj_eventos, 
        anotaciones=obj_anotaciones
    )
    
    assert len(senal.eventos.eventos) == 2
    assert senal.anotaciones.description[0] == "Pico"