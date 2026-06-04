#Testeo de la clase RawSignal
import pytest
import numpy as np
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones
from src.biosignals.signals.RawSignal import RawSignal

# ==========================================
# FIXTURES (Configuración reutilizable)
# ==========================================

@pytest.fixture
def dependencias_mock():
    """Genera instancias de las clases dependientes para usar en los tests."""
    info = Info(
        nombre_canales=['EEG1', 'EEG2', 'EMG1'],
        tipos_canales=['eeg', 'eeg', 'emg'],
        bad_channels=[],
        frecuencia_muestreo=250.0,
        duracion=10.0,
        info_experimento="Test",
        info_experimentador="Dev",
        eventos=[],
        frecuencia_linea=50.0,
        frecuencias_corte=[],
        frecuencias_notch=[]
    )
    eventos = Eventos([(100, 1), (200, 2)])
    anotaciones = Anotaciones(onset=[0.5], duration=[1.0], description=['estimulo'])
    
    # Matriz 2D: 3 canales x 2500 muestras (10 segundos a 250Hz)
    data = np.random.rand(3, 2500) 
    
    return info, eventos, anotaciones, data

@pytest.fixture
def raw_signal(dependencias_mock):
    """Genera un objeto RawSignal listo para testear."""
    info, eventos, anotaciones, data = dependencias_mock
    return RawSignal(info, eventos, anotaciones, data, first_samp=0)

# ==========================================
# TESTS DE CREACIÓN Y ATRIBUTOS BÁSICOS
# ==========================================

def test_creacion_correcta(raw_signal):
    """Verifica que el objeto se instancie con los datos correctos."""
    assert raw_signal.n_channels() == 3
    assert raw_signal.n_samples() == 2500
    assert raw_signal.duration() == 10.0

def test_creacion_error_dimensiones(dependencias_mock):
    """Verifica que lance ValueError si data no es 2D."""
    info, eventos, anotaciones, _ = dependencias_mock
    data_1d = np.random.rand(2500) # Matriz 1D
    
    with pytest.raises(ValueError, match="data debe tener forma de canales x muestras"):
        RawSignal(info, eventos, anotaciones, data_1d, 0)

def test_creacion_error_first_samp(dependencias_mock):
    """Verifica que lance ValueError si first_samp es negativo."""
    info, eventos, anotaciones, data = dependencias_mock
    with pytest.raises(ValueError, match="first_samp no puede ser negativo"):
        RawSignal(info, eventos, anotaciones, data, -1)

# ==========================================
# TESTS DE ACCESO A DATOS Y CANALES
# ==========================================

def test_get_data_completo(raw_signal):
    """Verifica el acceso a la matriz completa."""
    datos = raw_signal.get_data()
    assert datos.shape == (3, 2500)

def test_get_data_picks(raw_signal):
    """Verifica el acceso filtrando por nombres de canales específicos."""
    datos = raw_signal.get_data(picks=['EEG1', 'EMG1'])
    assert datos.shape == (2, 2500)

def test_getitem_comportamiento(raw_signal):
    """Verifica el funcionamiento del método mágico __getitem__."""
    canal_0 = raw_signal[0]
    assert canal_0.shape == (2500,)
    
    bloque = raw_signal[:, 100:200]
    assert bloque.shape == (3, 100)

def test_canal_inexistente(raw_signal):
    """Verifica el error al buscar un canal que no existe."""
    with pytest.raises(ValueError): # .index() en Python lanza ValueError si no encuentra el elemento
        raw_signal.get_channels(['CANAL_FALSO'])

# ==========================================
# TESTS DE MODIFICACIÓN DE LA SEÑAL
# ==========================================

def test_drop_channels(raw_signal):
    """Verifica la eliminación de canales."""
    raw_signal.drop_channels(['EEG2'])
    assert raw_signal.n_channels() == 2
    assert 'EEG2' not in raw_signal.info.nombre_canales

def test_picks_types(raw_signal):
    """Verifica la selección por tipo de canal."""
    raw_signal.picks_types('eeg')
    assert raw_signal.n_channels() == 2
    assert 'EMG1' not in raw_signal.info.nombre_canales

def test_crop_valido(raw_signal):
    """Verifica el recorte temporal de la señal."""
    # 250Hz -> 1 segundo = 250 muestras. Recorte de 1s a 3s = 2s de duración (500 muestras)
    raw_signal.crop(tmin=1.0, tmax=3.0)
    assert raw_signal.n_samples() == 500
    assert raw_signal.first_samp == 250

def test_crop_invalido_tmax(raw_signal):
    """Verifica error si tmin es mayor que tmax."""
    with pytest.raises(ValueError, match="tmin deber ser menor que tmax"):
        raw_signal.crop(tmin=5.0, tmax=2.0)

def test_filter(raw_signal):
    """Verifica que la función de filtrado se ejecute sin alterar las dimensiones."""
    shape_original = raw_signal.data.shape
    raw_signal.filter(tipo="media", ventana=5)
    assert raw_signal.data.shape == shape_original

# ==========================================
# TESTS DE MÉTODOS INFORMATIVOS Y ANOTACIONES
# ==========================================

def test_set_anotaciones(raw_signal):
    """Verifica la actualización de anotaciones."""
    nuevas_anotaciones = Anotaciones([1.0], [2.0], ['nuevo'])
    raw_signal.set_anotaciones(nuevas_anotaciones)
    assert raw_signal.anotaciones.description[0] == 'nuevo'

def test_describe(raw_signal):
    """Verifica la generación del diccionario de descripción."""
    desc = raw_signal.describe()
    assert desc['n_canales'] == 3
    assert desc['n_muestras'] == 2500
    assert desc['duración'] == 10.0
    assert desc['fs'] == 250.0

def test_str_representation(raw_signal):
    """Verifica la representación textual del objeto."""
    texto = str(raw_signal)
    assert "RawSignal" in texto
    assert "3 canales" in texto