import pytest
import numpy as np
import os

from src.biosignals.preprocesamiento.Dataset import Dataset
from src.biosignals.signals.RawSignal import RawSignal

# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def signal_dummy():
    """
    Crea una instancia real de RawSignal sin llamar a su __init__.
    Evita conflictos de firmas y de rutas de entorno.
    """
    # Creamos un objeto de la clase RawSignal saltándonos el constructor de los 5 argumentos
    obj = RawSignal.__new__(RawSignal)
    return obj

@pytest.fixture
def dataset_vacio():
    return Dataset(name="Dataset de Prueba", description="Tests unitarios")

@pytest.fixture
def archivo_csv(tmp_path):
    """Crea un CSV de prueba sin texto para simular datos puros."""
    ruta = tmp_path / "prueba_senales.csv"
    datos_simulados = np.array([[0.1, 0.2], [1.1, 1.2]])
    np.savetxt(ruta, datos_simulados, delimiter=',')
    return str(ruta)

@pytest.fixture
def archivo_txt(tmp_path):
    ruta = tmp_path / "prueba_un_canal.txt"
    datos_simulados = np.array([5.0, 6.0])
    np.savetxt(ruta, datos_simulados)
    return str(ruta)

# ==========================================
# TESTS
# ==========================================

def test_inicializacion_tipos_invalidos():
    with pytest.raises(TypeError):
        Dataset(name=123)  
    with pytest.raises(TypeError):
        Dataset(signals=["esto no es una senal"]) 

def test_agregar_senal(dataset_vacio, signal_dummy):
    assert len(dataset_vacio) == 0
    dataset_vacio.add_signal(signal_dummy)
    assert len(dataset_vacio) == 1

def test_agregar_senal_invalida(dataset_vacio):
    with pytest.raises(TypeError, match="instancia de RawSignal"):
        dataset_vacio.add_signal("Señal falsa")

def test_eliminar_senal(dataset_vacio, signal_dummy):
    dataset_vacio.add_signal(signal_dummy)
    dataset_vacio.add_signal(signal_dummy)
    dataset_vacio.remove_signal(0)
    assert len(dataset_vacio) == 1
    with pytest.raises(IndexError):
        dataset_vacio.remove_signal(99)

def test_obtener_senal_y_metodos_magicos(dataset_vacio, signal_dummy):
    dataset_vacio.add_signal(signal_dummy)
    assert dataset_vacio.get_signal(0) is signal_dummy
    assert dataset_vacio[0] is signal_dummy

def test_clear_dataset(dataset_vacio, signal_dummy):
    dataset_vacio.add_signal(signal_dummy)
    dataset_vacio.clear()
    assert len(dataset_vacio) == 0

def test_carga_de_senal_csv(archivo_csv):
    resultado = Dataset.carga_de_señal(archivo_csv)
    assert isinstance(resultado, dict)
    assert resultado["datos_crudos"].ndim == 2

def test_carga_de_senal_txt_un_canal(archivo_txt):
    resultado = Dataset.carga_de_señal(archivo_txt)
    assert resultado["datos_crudos"].shape[0] == 1

def test_carga_de_senal_archivo_no_encontrado():
    with pytest.raises(FileNotFoundError):
        Dataset.carga_de_señal("ruta/falsa/inexistente.csv")

def test_carga_formato_no_soportado(tmp_path):
    ruta_imagen = tmp_path / "imagen.jpg"
    ruta_imagen.write_text("datos falsos") 
    with pytest.raises(RuntimeError, match="Formato no soportado"):
        Dataset.carga_de_señal(str(ruta_imagen))

# ==========================================
# TEST CON TU ARCHIVO DE SEÑAL REAL
# ==========================================

def test_cargar_mi_propia_senal_real():
    # Tu ruta real detectada en la consola
    mi_ruta_real = "C:\\Users\\Luis Gonzalez\\Desktop\\ecg_registro_completo.csv" 
    
    if not os.path.exists(mi_ruta_real):
        pytest.skip("No se encuentra el archivo en el escritorio.")

    resultado = Dataset.carga_de_señal(mi_ruta_real)
    
    assert isinstance(resultado, dict)
    assert "datos_crudos" in resultado
    
    matriz_numpy = resultado["datos_crudos"]
    assert isinstance(matriz_numpy, np.ndarray)
    
    print("\n" + "="*40)
    print("   📊 INFO DE TU ARCHIVO REAL LEÍDO")
    print("="*40)
    print(f"Dimensiones de la matriz: {matriz_numpy.shape} -> (Canales, Muestras)")
    print(f"Cantidad de canales: {resultado['n_channels']}")
    print(f"Duración de la señal: {resultado['duracion']:.2f} segundos")
    print("="*40)

    