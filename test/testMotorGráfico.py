#Testeo de la clase MotorGráfico

import pytest
import numpy as np
import matplotlib
#sin abrir ventanas
matplotlib.use("Agg")

from biosignals.visualización.MotorGrafico import MotorGrafico
from biosignals.signals.RawSignal import RawSignal
from biosignals.info.Info import Info
from biosignals.eventos.Eventos import Eventos
from biosignals.eventos.Anotaciones import Anotaciones

#fixture es una señal de pruebas reutilizable

@pytest.fixture
def raw_signal_monocanal():

    info = Info(nombre_canales=["C1"], tipos_canales=["ECG"], bad_channels=[],frecuencia_muestreo=1000, duracion=1, info_experimento="Test para monocanal", info_experimentador="Federico", eventos = [], frecuencia_linea=50, frecuencias_corte=[1,40], frecuencias_notch=[50])
    eventos = Eventos([(100,1), (500,2)])
    anotaciones = Anotaciones
    data = np.random.rand(1,1000)

    return RawSignal(info,eventos,anotaciones,data,0)

def raw_signal_3canales():

    info = Info(nombre_canales=["C1","C2", "C3"], tipos_canales=["EEG","EEG","EEG"],bad_channels=[],frecuencia_muestreo=1000,duracion=1,info_experimento="Test para 3 canales", info_experimentador="Federico", eventos=[], frecuencia_linea=50,frecuencias_corte=[1,40],frecuencias_notch=[50])
    eventos = Eventos([])
    anotaciones = Anotaciones([],[],[])
    data = np.random.rand(3,1000)

    return RawSignal(info,eventos,anotaciones,data,0)

#test

def test_init(raw_signal_monocanal):

    motor = MotorGrafico(senal_actual=raw_signal_monocanal,epocas=None,modo_visualizacion="señal",canales_visibles=None,mostrar_anotaciones=False,rango_tiempo=None)
    assert motor.modo_visualizacion == "señal"

def test_graficar_monocanal(raw_signal_monocanal):

    motor = MotorGrafico(raw_signal_monocanal, None,"señal",None,False,None)
    motor.graficar_senal(mostrar=False)
    assert True

def test_graficar_3canales(raw_signal_3canales):

    motor = MotorGrafico(raw_signal_3canales,None,"señal",None,False,None)
    motor.graficar_senal(mostrar=False)
    assert True

def test_intervalo_valido(raw_signal_monocanal):
    motor = MotorGrafico(raw_signal_monocanal, None,"señal",None,False,None)
    motor.seleccionar_intervalo(0,0.5)
    assert motor.rango_tiempo == (0,0.5)

def test_intervalo_invalido(raw_signal_monocanal):
    motor = MotorGrafico(raw_signal_monocanal,None,"señal",None,False,None)
    with pytest.raises(ValueError):
        motor.seleccionar_intervalo(2,1)

def test_sin_senal():
    motor = MotorGrafico(None,None,"señal",None,False,None)
    with pytest.raises(ValueError):
        motor.graficar_senal()

def test_modo_invalido(raw_signal_monocanal):
    motor = MotorGrafico(raw_signal_monocanal,None,"incorrecto",None,False,None)
    with pytest.raises(ValueError):
        motor.actualizar()


