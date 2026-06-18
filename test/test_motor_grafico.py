#Testeo de la clase MotorGráfico
#Este test es para verificar que el objeto se cree correctamente, que se pueden graficar señales de 1xN, 3xN, que se pueden seleccionar intervalos válidos, que se detectan intervalos inválidos, que se detecta la ausencia de señal al graficar y que se detecta un modo de visualización inválido.
import pytest
import numpy as np
import matplotlib
#sin abrir ventanas
matplotlib.use("Agg")
from unittest.mock import patch
from src.biosignals.visualización.MotorGrafico import MotorGrafico
from src.biosignals.signals.RawSignal import RawSignal
from src.biosignals.info.Info import Info
from src.biosignals.eventos.Eventos import Eventos
from src.biosignals.eventos.Anotaciones import Anotaciones

#fixture es una señal de pruebas reutilizable

@pytest.fixture
def raw_signal_monocanal():

    info = Info(nombre_canales=["C1"], tipos_canales=["ECG"], bad_channels=[],frecuencia_muestreo=1000, duracion=1, info_experimento="Test para monocanal", info_experimentador="Federico", eventos = [], frecuencia_linea=50, frecuencias_corte=[1,40], frecuencias_notch=[50])
    eventos = Eventos([(100,1), (500,2)])
    anotaciones = Anotaciones([],[],[])
    data = np.random.rand(1,1000)
    print(f"Señal de prueba creada: {data.shape}")
    return RawSignal(info,eventos,anotaciones,data,0)

@pytest.fixture
def raw_signal_3canales():

    info = Info(nombre_canales=["C1","C2", "C3"], tipos_canales=["EEG","EEG","EEG"],bad_channels=[],frecuencia_muestreo=1000,duracion=1,info_experimento="Test para 3 canales", info_experimentador="Federico", eventos=[], frecuencia_linea=50,frecuencias_corte=[1,40],frecuencias_notch=[50])
    eventos = Eventos([])
    anotaciones = Anotaciones([],[],[])
    data = np.random.rand(3,1000)
    print(f"Señal de prueba creada: {data.shape}")
    return RawSignal(info,eventos,anotaciones,data,0)

@pytest.fixture
def raw_signal_8canales():

    info = Info(nombre_canales=["C1","C2","C3","C4","C5","C6","C7","C8"], tipos_canales=["EEG"]*8,bad_channels=[],frecuencia_muestreo=1000,duracion=1,info_experimento="Test para 8 canales", info_experimentador="Federico", eventos=[], frecuencia_linea=50,frecuencias_corte=[1,40],frecuencias_notch=[50])
    eventos = Eventos([])
    anotaciones = Anotaciones([],[],[])
    data = np.random.rand(8,1000)
    print(f"Señal de prueba creada: {data.shape}")
    return RawSignal(info,eventos,anotaciones,data,0)

@pytest.fixture
def raw_signal_32canales():

    info = Info(nombre_canales=[f"C{i}" for i in range(1,33)], tipos_canales=["EEG"]*32,bad_channels=[],frecuencia_muestreo=1000,duracion=1,info_experimento="Test para 32 canales", info_experimentador="Federico", eventos=[], frecuencia_linea=50,frecuencias_corte=[1,40],frecuencias_notch=[50])
    eventos = Eventos([])
    anotaciones = Anotaciones([],[],[])
    data = np.random.rand(32,1000)
    print(f"Señal de prueba creada: {data.shape}")
    return RawSignal(info,eventos,anotaciones,data,0)


#test

def test_init(raw_signal_monocanal):
    print("\nProbando inicialización del MotorGráfico")
    motor = MotorGrafico(senal_actual=raw_signal_monocanal,epocas=None,modo_visualizacion="señal",canales_visibles=None,mostrar_anotaciones=False,rango_tiempo=None)
    print(f"MotorGráfico inicializado con modo_visualizacion: {motor.modo_visualizacion}")
    assert motor.modo_visualizacion == "señal"
    assert motor.senal_actual is not None
    assert motor.mostrar_anotaciones is False

def test_graficar_monocanal(raw_signal_monocanal):
    print("\nProbando graficar señal monocanal")
    motor = MotorGrafico(raw_signal_monocanal, None,"señal",None,False,None)
    motor.graficar_senal(mostrar=False)
    print("Gráfico monocanal generado correctamente")
    assert True

def test_graficar_3canales(raw_signal_3canales):
    print("\nProbando graficar señal de 3 canales")
    motor = MotorGrafico(raw_signal_3canales,None,"señal",None,False,None)
    motor.graficar_senal(mostrar=False)
    print("Gráfico de 3 canales generado correctamente")
    assert True

def test_graficar_8canales(raw_signal_8canales):
    print("\nProbando graficar señal de 8 canales")
    motor = MotorGrafico(raw_signal_8canales,None,"señal",None,False,None)
    motor.graficar_senal(mostrar=False)
    print("Gráfico de 8 canales generado correctamente")
    assert True

def test_graficar_32canales(raw_signal_32canales):
    print("\nProbando graficar señal de 32 canales")
    motor = MotorGrafico(raw_signal_32canales,None,"señal",None,False,None)
    motor.graficar_senal(mostrar=False)
    print("Gráfico de 32 canales generado correctamente")
    assert True

def test_intervalo_valido(raw_signal_monocanal):
    print("Testando selección de intervalo válido")
    motor = MotorGrafico(raw_signal_monocanal, None,"señal",None,False,None)
    motor.seleccionar_intervalo(0,0.5)
    print(f"Intervalo seleccionado: {motor.rango_tiempo}")
    assert motor.rango_tiempo == (0,0.5)

def test_intervalo_invalido(raw_signal_monocanal):
    print("Testando selección de intervalo inválido")
    motor = MotorGrafico(raw_signal_monocanal,None,"señal",None,False,None)
    with pytest.raises(ValueError):
        motor.seleccionar_intervalo(2,1)
    print("Intervalo inválido correctamente detectado")

def test_sin_senal():
    print("Testando graficar sin señal")
    motor = MotorGrafico(None,None,"señal",None,False,None)
    with pytest.raises(ValueError):
        motor.graficar_senal()
    print("Error correctamente detectado al intentar graficar sin señal")

def test_modo_invalido(raw_signal_monocanal):
    print("Testando modo de visualización inválido")
    motor = MotorGrafico(raw_signal_monocanal,None,"incorrecto",None,False,None)
    with pytest.raises(ValueError):
        motor.actualizar()
    print("Error correctamente detectado para modo de visualización inválido")

@patch("src.biosignals.visualización.MotorGrafico.plt.show")
def test_graficar_por_renglones_exito(mock_show, raw_signal_3canales):
    print("\nProbando graficar multicanal por renglones")
    # Instanciamos el motor con tu fixture de 3 canales
    motor = MotorGrafico(raw_signal_3canales, None, "señal", None, False, None)
    
    # Ejecutamos el método con mostrar=True (comportamiento por defecto)
    motor.graficar_por_renglones()
    
    # Verificamos que llegó al final de la lógica y llamó a mostrar la figura
    mock_show.assert_called_once()
    print("Gráfico por renglones generado correctamente")

def test_graficar_por_renglones_sin_senal():
    print("\nProbando error al graficar renglones sin señal")
    motor = MotorGrafico(None, None, "señal", None, False, None)
    
    # Verificamos que ataje correctamente el error
    with pytest.raises(ValueError):
        motor.graficar_por_renglones()
    print("Error detectado correctamente")



