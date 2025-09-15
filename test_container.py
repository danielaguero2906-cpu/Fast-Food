import unittest
from unittest.mock import MagicMock
import tkinter as tk
from container import Container
from login import Ventas, Inventario, Clientes, AdminUsuarios

class MockControlador:
    def __init__(self, rol):
        self.usuario_rol = rol
        self.logout = MagicMock()

class TestContainer(unittest.TestCase):

    def setUp(self):
        # Crear raíz de Tkinter
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana
        self.controlador = MockControlador("admin")  # cambiar rol según test
        self.container = Container(self.root, self.controlador)

    def tearDown(self):
        self.container.destroy()
        self.root.destroy()

    def test_frames_admin(self):
        # Frames que debería tener admin
        expected_frames = ["Ventas", "Clientes", "Inventario", "AdminUsuarios"]
        for f in expected_frames:
            self.assertIn(f, self.container.frames)
            self.assertIsInstance(self.container.frames[f], tk.Frame)

    def test_frames_usuario(self):
        self.controlador.usuario_rol = "usuario"
        self.container.cargar_frames_por_rol()
        expected_frames = ["Ventas", "Clientes", "Inventario"]
        self.assertNotIn("AdminUsuarios", self.container.frames)
        for f in expected_frames:
            self.assertIn(f, self.container.frames)

    def test_show_frames_existente(self):
        self.container.show_frames("Ventas")
        # Si existe, no debería dar error
        self.assertIn("Ventas", self.container.frames)

    def test_show_frames_no_existente(self):
        import io, sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.container.show_frames("NoExiste")
        sys.stdout = sys.__stdout__
        self.assertIn("no existe", captured_output.getvalue())

    def test_logout_button_calls_controlador(self):
        self.container.btn_logout.invoke()
        self.controlador.logout.assert_called_once()

if __name__ == "__main__":
    unittest.main()
