#test_eventos
import pytest
import pandas as pd
from src.biosignals.eventos.Eventos import Eventos

#fixture
@pytest.fixture
def eventos_base():
    """
    Provee una instancia estándar de Eventos para usar en múltiples tests.
    """
    lista = [(100, 1), (250, 2), (400, 1)]
    mapeo = {1: "Estimulo", 2: "Respuesta"}
    return Eventos(eventos=lista, mapeo=mapeo)

#test de inicialización y validación

def test_inicializacion_correcta(eventos_base):
    """Verifica que el objeto se instancie con los datos correctos."""
    assert len(eventos_base) == 3
    assert eventos_base.eventos[0] == (100, 1)
    assert eventos_base.mapeo[1] == "Estimulo"

def test_inicializacion_tupla_invalida():
    """Verifica el contrato: rechaza eventos que no sean tuplas de 2 elementos."""
    eventos_malos = [(100, 1, "extra")]
    with pytest.raises(ValueError, match="Cada evento debe ser una tupla"):
        Eventos(eventos_malos)

def test_inicializacion_muestra_negativa():
    """Verifica el contrato: rechaza muestras negativas."""
    with pytest.raises(ValueError, match="La muestra no puede ser negativa"):
        Eventos([(-10, 1)])

def test_inicializacion_id_no_entero():
    """Verifica el contrato: el id_evento debe ser un entero."""
    with pytest.raises(TypeError, match="id_evento debe ser entero"):
        Eventos([(100, "A")])

#test de dunders
def test_iteracion(eventos_base):
    """Verifica que el objeto sea iterable."""
    eventos_extraidos = [ev for ev in eventos_base]
    assert eventos_extraidos == [(100, 1), (250, 2), (400, 1)]

def test_representacion_string(eventos_base):
    """Verifica que __str__ cuente correctamente los tipos de eventos."""
    texto = str(eventos_base)
    assert "3 eventos" in texto
    assert "1: 2" in texto # Hay dos eventos de tipo 1
    assert "2: 1" in texto # Hay un evento de tipo 2

# test de Add / Remove
def test_add_evento(eventos_base):
    """Asegura que se puedan agregar eventos pasando las validaciones."""
    eventos_base.add(500, 3)
    assert len(eventos_base) == 4
    assert eventos_base.eventos[-1] == (500, 3)

    #validaciones en el add()
    with pytest.raises(ValueError, match="no puede ser negativa"):
        eventos_base.add(-5, 1)
    with pytest.raises(TypeError, match="debe ser entero"):
        eventos_base.add(600, "Error")

def test_remove_evento(eventos_base):
    """Asegura que se eliminen eventos por índice de forma segura."""
    eventos_base.remove(1) # Elimina el (250, 2)
    assert len(eventos_base) == 2
    assert eventos_base.eventos[1] == (400, 1)
    #validación de límites
    with pytest.raises(IndexError, match="fuera de rango"):
        eventos_base.remove(99)
    with pytest.raises(IndexError, match="fuera de rango"):
        eventos_base.remove(-10)

#test de detaframe y búsqueda
def test_get_events(eventos_base):
    """Asegura la correcta conversión a DataFrame."""
    df = eventos_base.get_events()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['muestra', 'id_evento']
    assert len(df) == 3

def test_find_evento(eventos_base):
    """Verifica el filtrado de eventos mediante DataFrame."""
    df_filtrado = eventos_base.find(1)
    assert len(df_filtrado) == 2
    assert all(df_filtrado['id_evento'] == 1)

    #buscar un evento que no existe
    df_vacio = eventos_base.find(99)
    assert len(df_vacio) == 0

def test_get_label(eventos_base):
    """Verifica la obtención de etiquetas a partir del mapeo."""
    assert eventos_base.get_label(1) == "Estimulo"
    assert eventos_base.get_label(99) == "Desconocido"

#test de archivos (guardar y cargar)
def test_save_y_load_csv(eventos_base, tmp_path):
    """Prueba el ciclo completo de guardar y cargar usando un archivo temporal."""
    #tmp_path es un directorio temporal proveído por pytest
    archivo_csv = tmp_path / "eventos_test.csv"
    #guardar
    eventos_base.save(str(archivo_csv))
    assert archivo_csv.exists()
    #cargar (usamos la clase pura ya que es un @classmethod)
    eventos_cargados = Eventos.load(str(archivo_csv))
    #validar consistencia de los datos
    assert len(eventos_cargados) == 3
    assert eventos_cargados.eventos == eventos_base.eventos

def test_save_formatos_soportados(eventos_base, tmp_path):
    """Verifica que los formatos txt y json no generen errores."""
    archivo_txt = tmp_path / "test.txt"
    archivo_json = tmp_path / "test.json"
    
    eventos_base.save(str(archivo_txt))
    eventos_base.save(str(archivo_json))
    
    assert archivo_txt.exists()
    assert archivo_json.exists()

def test_save_formato_no_soportado(eventos_base):
    """Verifica que se rechacen extensiones no manejadas."""
    with pytest.raises(ValueError, match="Formato no soportado"):
        eventos_base.save("archivo_invalido.excel")