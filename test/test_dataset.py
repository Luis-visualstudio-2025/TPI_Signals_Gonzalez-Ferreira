import unittest
from src.biosignals.preprocesamiento.Dataset import Dataset

# Intentamos importar la clase real, si falla usamos el fallback
try:
    from src.biosignals.signals.RawSignal import RawSignal
except ImportError:
    class RawSignal:
        pass

# CREACIÓN DEL MOCK: Hereda de RawSignal para pasar el filtro isinstance()
# pero redefine el __init__ para que no nos pida parámetros obligatorios.
class MockSignal(RawSignal):
    def __init__(self):
        pass # No pide nada, ideal para pruebas rápidas
    
    def n_channels(self) -> int:
        return 2
    
    def n_samples(self) -> int:
        return 1000

class TestDataset(unittest.TestCase):
    def setUp(self):
        """Preparamos un dataset y una señal simulada antes de cada test."""
        self.ds = Dataset(name="TestSet", description="Dataset de prueba")
        # Usamos nuestro objeto simulado seguro
        self.s1 = MockSignal()

    # 1. Test de inicialización y propiedades (name, description, info)
    def test_properties(self):
        self.ds.name = "Nuevo Nombre"
        self.ds.description = "Nueva Desc"
        self.assertEqual(self.ds.name, "Nuevo Nombre")
        self.assertEqual(self.ds.description, "Nueva Desc")
        with self.assertRaises(TypeError):
            self.ds.name = 123  # Debe fallar si no es un string

    # 2. Test de add_signal
    def test_add_signal(self):
        self.ds.add_signal(self.s1)
        self.assertEqual(len(self.ds), 1)
        
        # Validamos que rechace cosas que no sean señales
        with self.assertRaises(TypeError):
            self.ds.add_signal("No soy una señal")

    # 3. Test de get_signal (y __getitem__ indirectamente)
    def test_get_signal(self):
        self.ds.add_signal(self.s1)
        self.assertEqual(self.ds.get_signal(0), self.s1)
        self.assertEqual(self.ds[0], self.s1)  # Prueba el uso de corchetes []

    # 4. Test de remove_signal
    def test_remove_signal(self):
        self.ds.add_signal(self.s1)
        self.ds.remove_signal(0)
        self.assertEqual(len(self.ds), 0)
        
        # Validamos error si el índice no existe
        with self.assertRaises(IndexError):
            self.ds.remove_signal(99)

    # 5. Test de clear
    def test_clear(self):
        self.ds.add_signal(self.s1)
        self.ds.clear()
        self.assertEqual(len(self.ds), 0)

    # 6. Test de __len__
    def test_len(self):
        self.assertEqual(len(self.ds), 0)
        self.ds.add_signal(self.s1)
        self.assertEqual(len(self.ds), 1)

    # 7. Test de summary (Verificamos que ejecute el flujo visual sin romperse)
    def test_summary(self):
        self.ds.add_signal(self.s1)
        try:
            self.ds.summary()
        except Exception as e:
            self.fail(f"summary() falló inesperadamente: {e}")

if __name__ == '__main__':
    unittest.main()
    