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
        """El rol admin debería tener todos los frames."""
        expected_frames = ["Ventas", "Clientes", "Inventario", "AdminUsuarios"]
        for f in expected_frames:
            self.assertIn(f, self.container.frames)
            self.assertIsInstance(self.container.frames[f], tk.Frame)

    def test_frames_usuario(self):
        """El rol usuario NO debería tener AdminUsuarios."""
        self.controlador.usuario_rol = "usuario"
        self.container.cargar_frames_por_rol()
        expected_frames = ["Ventas", "Clientes", "Inventario"]
        self.assertNotIn("AdminUsuarios", self.container.frames)
        for f in expected_frames:
            self.assertIn(f, self.container.frames)

    def test_show_frame_existente(self):
        """show_frame debería funcionar con un frame válido."""
        self.container.show_frame("Ventas")
        self.assertIn("Ventas", self.container.frames)

    def test_show_frame_no_existente(self):
        """show_frame debería avisar si el frame no existe."""
        import io, sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.container.show_frame("NoExiste")
        sys.stdout = sys.__stdout__
        self.assertIn("no existe", captured_output.getvalue().lower())

    def test_logout_button_calls_controlador(self):
        """El botón Cerrar Sesión debería llamar a logout del controlador."""
        # Buscar el botón "Cerrar Sesión" en los hijos
        logout_button = None
        for child in self.container.winfo_children():
            for grandchild in child.winfo_children():
                if isinstance(grandchild, tk.Button) and grandchild.cget("text") == "Cerrar Sesión":
                    logout_button = grandchild
                    break

        self.assertIsNotNone(logout_button, "No se encontró el botón de Cerrar Sesión")
        logout_button.invoke()
        self.controlador.logout.assert_called_once()

if __name__ == "__main__":
    unittest.main()
