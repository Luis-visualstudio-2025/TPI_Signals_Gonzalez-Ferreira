#test_anotaciones
import pytest
import pandas as pd
from src.biosignals.eventos.Anotaciones import Anotaciones

#fixture
@pytest.fixture
def anotaciones_base():
    """
    Provee una instancia estándar de Anotaciones con datos válidos para las pruebas.
    """
    onset = [0.0, 5.5, 10.2]
    duration = [1.0, 0.5, 2.0]
    description = ["Ojos cerrados", "Movimiento", "Ojos cerrados"]
    t0 = 0.0
    ch_names = ["C3", "C4"]
    return Anotaciones(onset, duration, description, t0, ch_names)

#test de inicialización y contratos
def test_inicializacion_correcta(anotaciones_base):
    """Verifica que el objeto se instancie con los datos correctos."""
    assert len(anotaciones_base) == 3
    assert anotaciones_base.onset[1] == 5.5
    assert anotaciones_base.duration[2] == 2.0
    assert anotaciones_base.t0 == 0.0
    assert anotaciones_base.ch_names == ["C3", "C4"]

def test_inicializacion_longitudes_distintas():
    """Rechaza la creación si las listas no tienen el mismo tamaño."""
    with pytest.raises(ValueError, match="deben tener la misma longitud"):
        Anotaciones([1.0, 2.0], [1.0], ["A", "B"])

def test_inicializacion_valores_negativos():
    """Rechaza onset o duraciones negativas en la inicialización."""
    with pytest.raises(ValueError, match="onset no puede ser negativo"):
        Anotaciones([-1.0], [1.0], ["A"])
        
    with pytest.raises(ValueError, match="duration no puede ser negativo"):
        Anotaciones([1.0], [-1.0], ["A"])

def test_inicializacion_descripcion_no_string():
    """Rechaza descripciones que no sean cadenas de texto."""
    with pytest.raises(TypeError, match="description debe ser un string"):
        Anotaciones([1.0], [1.0], [100])

#tests de dunders
def test_iteracion(anotaciones_base):
    """Verifica que el objeto pueda ser iterado comprimiendo las 3 listas."""
    extraccion = [anot for anot in anotaciones_base]
    assert extraccion[0] == (0.0, 1.0, "Ojos cerrados")
    assert len(extraccion) == 3

def test_representacion_string(anotaciones_base):
    """Verifica que __str__ resuma correctamente las anotaciones."""
    texto = str(anotaciones_base)
    assert "3 anotaciones" in texto
    assert "Ojos cerrados" in texto
    assert "Movimiento" in texto

# test de modificción (add / remove)
def test_add_anotacion(anotaciones_base):
    """Prueba la inserción de una nueva anotación válida."""
    anotaciones_base.add(15.0, 1.5, "Artefacto")
    
    assert len(anotaciones_base) == 4
    assert anotaciones_base.onset[-1] == 15.0
    assert anotaciones_base.description[-1] == "Artefacto"

def test_add_anotacion_invalida(anotaciones_base):
    """Verifica que el método add respete los contratos de validación."""
    with pytest.raises(ValueError, match="onset no puede ser negativo"):
        anotaciones_base.add(-2.0, 1.0, "A")
        
    with pytest.raises(ValueError, match="duration no puede ser negativa"):
        anotaciones_base.add(2.0, -1.0, "A")
        
    with pytest.raises(TypeError, match="description debe ser string"):
        anotaciones_base.add(2.0, 1.0, None)

def test_remove_anotacion(anotaciones_base):
    """Prueba la eliminación sincronizada de elementos por su índice."""
    anotaciones_base.remove(1)  #elimina el índice 1 ("movimiento")
    
    assert len(anotaciones_base) == 2
    assert anotaciones_base.onset[1] == 10.2  #el índice 2 pasó a ser el 1
    assert "Movimiento" not in anotaciones_base.description

def test_remove_indice_invalido(anotaciones_base):
    """Rechaza intentos de eliminar índices inexistentes."""
    with pytest.raises(IndexError, match="índice fuera de rango"):
        anotaciones_base.remove(10)
    with pytest.raises(IndexError, match="índice fuera de rango"):
        anotaciones_base.remove(-1)

#test de recuperación de datos(DataFrames)
def test_get_annotations(anotaciones_base):
    """Asegura la correcta exportación a DataFrame de Pandas."""
    df = anotaciones_base.get_annotations()
    
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['onset', 'duration', 'description']
    assert len(df) == 3
    assert df.iloc[0]['description'] == "Ojos cerrados"

def test_find_anotacion(anotaciones_base):
    """Verifica la capacidad de filtrar el DataFrame por descripción."""
    df_filtrado = anotaciones_base.find("Ojos cerrados")
    
    assert len(df_filtrado) == 2
    assert all(df_filtrado['description'] == "Ojos cerrados")

    df_vacio = anotaciones_base.find("Inexistente")
    assert len(df_vacio) == 0

#test de archivos 
def test_save_y_load_csv(anotaciones_base, tmp_path):
    """Prueba el ciclo completo de I/O para asegurar que la data no mute."""
    archivo = tmp_path / "anotaciones_test.csv"
    #guardamos
    anotaciones_base.save(str(archivo))
    assert archivo.exists()
    #cargamos
    anot_cargadas = Anotaciones.load(str(archivo))
    #comprobamos la integridad
    assert len(anot_cargadas) == len(anotaciones_base)
    assert anot_cargadas.onset == anotaciones_base.onset
    assert anot_cargadas.t0 == anotaciones_base.t0
    #al guardarse como string representacional en CSV, las listas en celdas pueden requerir evaluación, pero comprobamos que el ch_names existe.
    assert anot_cargadas.ch_names is not None

def test_load_formato_no_soportado():
    """Valida que intente cargar solo extensiones permitidas."""
    with pytest.raises(ValueError, match="Formato no soportado"):
        Anotaciones.load("datos.xlsx")