import pytest
import numpy as np

# Importamos tu arquitectura real completa
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.preprocesamiento.SignalProcessor import SignalProcessor

#fixture
@pytest.fixture
def processor():
    """Genera una RawSignal real en memoria y la inyecta al SignalProcessor."""
    
    #info 
    info = Info(
        frecuencia_muestreo=250.0, 
        nombre_canales=["CH1", "CH2"], 
        tipos_canales=["eeg", "eeg"]
    )
    
    #eventos y anotaciones (Vacíos o mínimos para no interferir con el procesador)
    eventos = Eventos([]) 
    anotaciones = Anotaciones(onset=[], duration=[], description=[])
    
    #datos 2D (2 canales x 1000 muestras)
    # CH1: constante de unos. CH2: rampa ascendente.
    data = np.array([
        np.ones(1000), 
        np.arange(1000, dtype=float)])
    
    #instanciamos la señal 
    signal_real = RawSignal(
        info=info, 
        eventos=eventos, 
        anotaciones=anotaciones, 
        data=data, 
        first_samp=0)
    
    #entregamos el SignalProcessor
    return SignalProcessor(signal_real)

#test de filtrado
def test_apply_lowpass_valido(processor):
    """Verifica el filtrado pasabajos con una ventana válida."""
    procesada = processor.apply_lowpass(ventana=5)
    
    #comprueba inmutabilidad: el objeto procesado NO debe ser el original
    assert procesada is not processor.signal  
    #mantiene las dimensiones originales
    assert procesada.data.shape == (2, 1000)     

def test_apply_lowpass_invalido(processor):
    """Verifica que rechace ventanas negativas o cero."""
    with pytest.raises(ValueError, match="ventana debe ser positiva"):
        processor.apply_lowpass(ventana=0)
    with pytest.raises(ValueError, match="ventana debe ser positiva"):
        processor.apply_lowpass(ventana=-5)

def test_apply_highpass_valido(processor):
    """Verifica el filtrado pasaltos."""
    procesada = processor.apply_highpass(ventana=5)
    assert procesada.data.shape == (2, 1000)

#test del filtro notch
def test_apply_notch_valido(processor):
    """Verifica que el filtro notch se aplique correctamente."""
    procesada = processor.apply_notch(freq=50.0, Q=30)
    
    assert procesada is not processor.signal
    assert procesada.data.shape == (2, 1000)

def test_apply_notch_freq_negativa(processor):
    """Verifica validación de frecuencia positiva."""
    with pytest.raises(ValueError, match="La frecuencia debe ser positiva"):
        processor.apply_notch(freq=-10.0)

def test_apply_notch_nyquist(processor):
    """Verifica que respete el Teorema de Nyquist (fs/2)."""
    #fs es 250, fs/2 es 125. Si pasamos 130, debe fallar.
    with pytest.raises(ValueError, match="criterio de Nyquist"):
        processor.apply_notch(freq=130.0)

def test_apply_notch_q_invalido(processor):
    """Verifica que Q sea estrictamente positivo."""
    with pytest.raises(ValueError, match="Q debe ser positivo"):
        processor.apply_notch(freq=25.0, Q=0)

#test de normalización
def test_normalize(processor):
    """Verifica que los datos queden escalados en el rango [0, 1]."""
    procesada = processor.normalize()
    
    #validamos el Canal 2 (índice 1) que era una rampa ascendente
    canal_2 = procesada.data[1]
    assert np.isclose(np.nanmin(canal_2), 0.0)
    assert np.isclose(np.nanmax(canal_2), 1.0)


#test de resample
def test_resample(processor):
    """Verifica el cambio de frecuencia y alteración del número de muestras."""
    nueva_fs = 125.0 #reducimos a la mitad
    procesada = processor.resample(nueva_fs)
    
    #verificamos que se actualice la info de la nueva señal devuelta
    assert procesada.info.frecuencia_muestreo == 125.0
    #verificamos que la cantidad de muestras se haya reducido a la mitad (500)
    assert procesada.data.shape[1] == 500

#test de baseline
def test_remove_baseline(processor):
    """Verifica que la media de la señal procesada sea virtualmente cero."""
    procesada = processor.remove_baseline()
    #calculamos la media del canal 2 (rampa de 0 a 999)
    media_canal_2 = np.mean(procesada.data[1])
    #la media de los datos corregidos debe ser extremadamente cercana a 0
    assert np.isclose(media_canal_2, 0.0, atol=1e-10)

#test de representación textual
def test_str_representation(processor):
    """Verifica que __str__ devuelva la información esperada."""
    texto = str(processor)
    assert "SignalProcessor" in texto
    assert "2 canales" in texto