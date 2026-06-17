import pytest
import numpy as np
import os

# Ajusta esta importación según la ruta real en tu proyecto
from src.biosignals.preprocesamiento.Dataset import Dataset
from src.biosignals.signals.RawSignal import RawSignal

# ==========================================
# FIXTURES (Configuración previa para los tests)
# ==========================================

@pytest.fixture
def signal_dummy():
    """
    Creamos una clase temporal que hereda de RawSignal.
    Esto engaña perfectamente a 'isinstance()' pasando la validación,
    pero anulamos su constructor (__init__) para que no pida los 5 parámetros.
    """
    class DummySignal(RawSignal):
        def __init__(self):
            # No hacemos nada, evitamos el __init__ original
            pass
            
    return DummySignal()

@pytest.fixture
def dataset_vacio():
    """Retorna un Dataset inicializado vacío."""
    return Dataset(name="Dataset de Prueba", description="Tests unitarios")

@pytest.fixture
def archivo_csv(tmp_path):
    """Crea un archivo CSV temporal con una matriz de 2 canales x 5 muestras."""
    ruta = tmp_path / "prueba_senales.csv"
    datos_simulados = np.array([
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [1.1, 1.2, 1.3, 1.4, 1.5]
    ])
    np.savetxt(ruta, datos_simulados, delimiter=',')
    return str(ruta)

@pytest.fixture
def archivo_txt(tmp_path):
    """Crea un archivo TXT temporal de 1 solo canal x 4 muestras."""
    ruta = tmp_path / "prueba_un_canal.txt"
    datos_simulados = np.array([5.0, 6.0, 7.0, 8.0])
    np.savetxt(ruta, datos_simulados)
    return str(ruta)

# ==========================================
# TESTS DE ENCAPSULAMIENTO E INICIALIZACIÓN
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

# ==========================================
# TESTS DE GESTIÓN DE LA LISTA
# ==========================================

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

# ==========================================
# TESTS DE CARGA DE ARCHIVOS (Módulo Numpy)
# ==========================================

def test_carga_de_senal_csv(archivo_csv):
    resultado = Dataset.carga_de_señal(archivo_csv)
    assert isinstance(resultado, dict)
    assert resultado["datos_crudos"].shape == (2, 5) 

def test_carga_de_senal_txt_un_canal(archivo_txt):
    resultado = Dataset.carga_de_señal(archivo_txt)
    assert resultado["datos_crudos"].shape == (1, 4)

def test_carga_de_senal_archivo_no_encontrado():
    with pytest.raises(FileNotFoundError):
        Dataset.carga_de_señal("ruta/falsa/inexistente.csv")

def test_carga_formato_no_soportado(tmp_path):
    ruta_imagen = tmp_path / "imagen.jpg"
    ruta_imagen.write_text("datos falsos") 
    with pytest.raises(RuntimeError, match="Formato no soportado"):
        Dataset.carga_de_señal(str(ruta_imagen))

# ==========================================
# TEST PARA TU SEÑAL REAL
# ==========================================

def test_cargar_mi_propia_senal():
    """
    Prueba que carga tu archivo de señal real.
    """
    # 1. REEMPLAZA ESTA RUTA CON LA UBICACIÓN DE TU ARCHIVO REAL
    mi_ruta = "C:/ruta/a/mi/archivo/de/senal.txt" # <-- ¡Modifica esto!
    
    # Previene que el test falle si aún no has modificado la ruta de arriba
    if mi_ruta == "C:/ruta/a/mi/archivo/de/senal.txt" or not os.path.exists(mi_ruta):
        pytest.skip(f"Aún no has configurado una ruta válida, o el archivo no existe en: {mi_ruta}")

    # 2. Ejecutamos tu función con el archivo real
    resultado = Dataset.carga_de_señal(mi_ruta)
    
    # 3. Verificamos que contenga los datos
    assert isinstance(resultado, dict)
    assert "datos_crudos" in resultado
    
    # 4. Imprimimos el resultado para que veas qué leyó.
    # Para ver este print al correr pytest, usa el comando: pytest -v -s
    print("\n--- RESULTADOS DE MI SEÑAL ---")
    print(f"Formato de la matriz leída: {resultado['datos_crudos'].shape} (Canales, Muestras)")
    print(f"Canales detectados: {resultado['n_channels']}")
    print("------------------------------")