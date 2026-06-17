import pytest
import numpy as np
from unittest.mock import MagicMock

from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.epocas.Epocas import Epocas 

#fixture
@pytest.fixture
def configuracion_base():
    """
    Fixture que provee objetos Info, Eventos, RawSignal y ndarrays 
    perfectamente instanciados según las clases reales para las pruebas.
    """
    #instanciamos
    info = Info(
        frecuencia_muestreo=250.0,
        nombre_canales=["C3", "Cz", "C4"],
        tipos_canales=["eeg", "eeg", "eeg"],
        duracion=4.0)

    #creamos eventos
    lista_eventos = [(200, 1), (600, 2)]
    mapeo_eventos = {1: "Estimulo Visual", 2: "Respuesta Motora"}
    eventos_obj = Eventos(eventos=lista_eventos, mapeo=mapeo_eventos)
    #creamos un array de eventos crudo 
    eventos_array = np.array([[200, 1], [600, 2]])
    #mock de Anotaciones 
    anotaciones_mock = MagicMock(spec=Anotaciones)
    #creamos los datos de la señal (3 canales, 1000 muestras -> 4 segundos)
    data = np.random.randn(3, 1000)
    #instanciamos raw
    raw = RawSignal(
        info=info,
        eventos=eventos_obj,
        anotaciones=anotaciones_mock,
        data=data,
        first_samp=0)
    return raw, eventos_obj, eventos_array

#test de creación y validación
def test_creacion_epocas_con_objeto_eventos(configuracion_base):
    """Verifica la creación pasando una instancia formal de la clase Eventos."""
    raw, eventos_obj, _ = configuracion_base
    #tmin = -0.2 (50 muestras previas), tmax = 0.5 (125 muestras posteriores)
    #total de muestras por época = 175
    epocas = Epocas(signal=raw, eventos=eventos_obj, tmin=-0.2, tmax=0.5)
    out = epocas.get_data()
    assert out.shape == (2, 3, 175)
    assert len(epocas) == 2

def test_creacion_epocas_con_ndarray(configuracion_base):
    """Verifica la creación pasando un numpy array directamente."""
    raw, _, eventos_array = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_array, tmin=-0.2, tmax=0.5)
    assert epocas.get_data().shape == (2, 3, 175)

def test_creacion_epocas_tipo_senal_invalida(configuracion_base):
    """Asegura el rechazo si la señal no es RawSignal."""
    _, eventos_obj, _ = configuracion_base
    with pytest.raises(TypeError, match="debe ser una instancia o heredar de RawSignal"):
        Epocas(signal="StringAleatorio", eventos=eventos_obj)

def test_eventos_dimension_invalida(configuracion_base):
    """Asegura el rechazo si el array de eventos no tiene 2 columnas."""
    raw, _, _ = configuracion_base
    eventos_malos = np.array([1, 2, 3])  # Array 1D
    with pytest.raises(ValueError, match="dimensiones \\(n_eventos, 2\\)"):
        Epocas(signal=raw, eventos=eventos_malos)

#test de propiedades (encapsulamiento)
def test_propiedades_tmin_tmax(configuracion_base):
    """Comprueba el encapsulamiento y control de flujo de tmin y tmax."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj, tmin=-0.1, tmax=0.3)
    #modificación válida
    epocas.tmin = 0.0
    assert epocas.tmin == 0.0
    #modificaciones inválidas (disparan ValueError)
    with pytest.raises(ValueError, match="menor que 'tmax'"):
        epocas.tmin = 0.5  # 0.5 >= 0.3 (tmax actual)
    with pytest.raises(ValueError, match="mayor que 'tmin'"):
        epocas.tmax = -0.2 # -0.2 <= 0.0 (tmin actual)


#test de procesamiento y métodos
def test_seleccion_por_id_eventos_y_picks(configuracion_base):
    """Valida el filtrado simultáneo de canales (picks) y tipos de eventos."""
    raw, eventos_obj, _ = configuracion_base
    #extraemos solo el evento 1 y los canales C3 y C4
    epocas = Epocas(signal=raw, eventos=eventos_obj, id_eventos=1, picks=["C3", "C4"])
    out = epocas.get_data()
    #1 época resultante, 2 canales seleccionados, 175 muestras (tmin -0.2 a 0.5 = 0.7s * 250Hz)
    assert out.shape == (1, 2, 175)

def test_promedio(configuracion_base):
    """Comprueba el colapso de la dimensión temporal calculando el ERP (promedio)."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj)
    promedio_epocas = epocas.promedio()
    out = promedio_epocas.get_data()
    
    assert out.shape == (1, 3, 175)
    assert isinstance(promedio_epocas, Epocas)

def test_recortar(configuracion_base):
    """Comprueba el recorte temporal interno de las épocas."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj, tmin=-0.2, tmax=0.5)
    #recortamos a una ventana estricta de 0.0s a 0.2s (50 muestras)
    epocas_recortadas = epocas.recortar(0.0, 0.2)
    
    assert epocas_recortadas.tmin == 0.0
    assert epocas_recortadas.tmax == 0.2
    assert epocas_recortadas.get_data().shape[2] == 50

def test_eliminar_canales(configuracion_base):
    """Prueba la eliminación estructural de canales específicos."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj)
    epocas.eliminar_canales(["Cz"])
    
    assert epocas.get_data().shape[1] == 2
    assert "Cz" not in epocas.signal.info.nombre_canales
    
    #comprobar manejo de errores con canal no existente
    with pytest.raises(ValueError, match="Imposible eliminar canales no existentes"):
        epocas.eliminar_canales(["Inexistente"])

def test_tiempo_frecuencia(configuracion_base):
    """Verifica que el espectro (FFT) retorne valores reales de igual dimensión."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj)
    espectro = epocas.tiempo_frecuencia()
    
    assert espectro.shape == epocas.get_data().shape
    assert not np.iscomplexobj(espectro) # np.abs garantiza salida real

def test_mapeo_y_cambio_ids(configuracion_base):
    """Evalúa la interacción de las etiquetas con la clase Eventos."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj)
    
    #verificar extracción de etiquetas
    mapeo = epocas.obtener_mapeo_id_evento()
    assert mapeo[1] == "Estimulo Visual"
    
    #modificación dinámica de IDs (1 -> 10, 2 -> 20)
    epocas.cambiar_id_eventos({1: 10, 2: 20})
    nuevo_mapeo = epocas.obtener_mapeo_id_evento()
    
    assert 10 in nuevo_mapeo and 20 in nuevo_mapeo

def test_criterio_rechazo_reject(configuracion_base):
    """Verifica el algoritmo de rechazo automático por Peak-to-Peak."""
    raw, eventos_obj, _ = configuracion_base    
    #introducimos un artefacto masivo en el canal C3, alrededor de la muestra 200 (Época 1)
    raw.data[0, 150:250] = 500.0 
    #umbral de tolerancia de 10.0 en C3
    epocas = Epocas(signal=raw, eventos=eventos_obj, tmin=-0.2, tmax=0.5, reject={"C3": 10.0})
    #la época 1 debe haber sido rechazada por superar el umbral
    assert len(epocas) == 1

def test_dunders(configuracion_base):
    """Asegura que los métodos mágicos informativos funcionen."""
    raw, eventos_obj, _ = configuracion_base
    epocas = Epocas(signal=raw, eventos=eventos_obj)
    assert len(epocas) == 2
    
    descripcion = str(epocas)
    assert "2 épocas" in descripcion
    assert "3 canales" in descripcion