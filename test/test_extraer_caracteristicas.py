#test_extraer_caracteristicas
import pytest
import numpy as np
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.info.Info import Info
from src.biosignals.preprocesamiento.ExtraerCaracteristicas import ExtraerCaracteristicas 
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

#fixture
@pytest.fixture
def senal_prueba():
    """Genera una RawSignal de prueba para inyectar al extractor."""
    info = Info(
        frecuencia_muestreo=250.0,
        nombre_canales=["CH1", "CH2"],
        tipos_canales=["eeg", "eeg"],
        bad_channels=[],
        duracion=4.0 #1000 muestras / 250 Hz = 4.0 s
    )
    
    #señal de 2 canales y 1000 muestras
    data = np.array([
        np.zeros(1000),
        np.random.rand(1000)
    ])
    
    #creamos el dummy de Eventos pasándole una lista vacía
    eventos_dummy = Eventos(eventos=[])
    
    #creamos el dummy de Anotaciones pasándole 3 listas vacías (cumple que tengan = longitud)
    anotaciones_dummy = Anotaciones(onset=[], duration=[], description=[])
    
    return RawSignal(
        info=info, 
        eventos=eventos_dummy,
        anotaciones=anotaciones_dummy,
        data=data, 
        first_samp=0
    )

@pytest.fixture
def extractor(senal_prueba):
    """Fixture que devuelve la clase instanciada con la señal."""
    return ExtraerCaracteristicas(senal_prueba)

#test
def test_init_valido(senal_prueba):
    """Verifica que se inicialice correctamente con un RawSignal."""
    ext = ExtraerCaracteristicas(senal_prueba)
    assert ext.signal is senal_prueba
    assert isinstance(ext.caracteristicas, dict)

def test_init_invalido():
    """Verifica que falle si se le pasa algo que no es RawSignal."""
    with pytest.raises(TypeError, match="signal deber ser RawSignal"):
        ExtraerCaracteristicas("Esto es un string, no una señal")

def test_get_signal(extractor, senal_prueba):
    """Verifica que retorne los datos correctos."""
    datos = extractor.get_signal()
    assert np.array_equal(datos, senal_prueba.data)

def test_mean(extractor):
    """Verifica el cálculo de la media temporal."""
    medias = extractor.mean()
    assert medias.shape == (2,) #una media por cada canal
    assert medias[0] == 0.0 #el canal 1 era de puros ceros

def test_std(extractor):
    """Verifica el cálculo de la desviación estándar temporal."""
    desviaciones = extractor.std()
    assert desviaciones.shape == (2,)
    assert desviaciones[0] == 0.0 #el canal 1 no tiene variación

def test_get_hilbert_transform(extractor):
    """Verifica que la transformada de Hilbert retorne la envolvente correcta."""
    envolvente = extractor.get_hilbert_transform()
    #la salida debe tener las mismas dimensiones que la entrada
    assert envolvente.shape == (2, 1000)
    #como es np.abs(), no debe haber valores negativos
    assert np.all(envolvente >= 0)

def test_get_spectrogram(extractor):
    """Verifica que el espectrograma devuelva las 3 matrices correctas."""
    f, t, Sxx = extractor.get_spectrogram(ch_name="CH1")
    #verificamos que no estén vacíos y sean arrays de NumPy
    assert isinstance(f, np.ndarray)
    assert isinstance(t, np.ndarray)
    assert isinstance(Sxx, np.ndarray) #Sxx es la matriz que contiene los valores del espectrograma en sí
    #la matriz del espectrograma Sxx debe tener shape (len(f), len(t))
    assert Sxx.shape == (len(f), len(t))

def test_getFourierTransform(extractor):
    """Verifica que la FFT retorne frecuencias y amplitudes coherentes."""
    freqs, fft_values = extractor.getFourierTransform()
    
    #para la transformada real (rfft), la longitud esperada es n/2 + 1
    #n es 1000 muestras, por lo que esperamos 501 valores de frecuencia
    expected_length = 1000 // 2 + 1
    assert len(freqs) == expected_length
    assert fft_values.shape == (2, expected_length) #2 canales, 501 frecuencias
    #la frecuencia máxima en la rfft debería ser aproximadamente la de Nyquist (fs / 2)
    fs = extractor.signal.info.frecuencia_muestreo
    assert np.isclose(freqs[-1], fs / 2)