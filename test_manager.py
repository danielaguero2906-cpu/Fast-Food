import unittest
import tkinter as tk
from manager import Manager

class TestManager(unittest.TestCase):
    def setUp(self):
        # Crear root oculto para no mostrar ventana
        self.root = tk.Tk()
        self.root.withdraw()
        self.manager = Manager()

    def tearDown(self):
        self.manager.destroy()
        self.root.destroy()

    def test_show_frame_login_exists(self):
        """Verifica que el frame Login exista y se pueda mostrar."""
        self.manager.show_frame("Login")
        self.assertIn("Login", self.manager.frames)
    
    def test_cargar_container_admin(self):
        """Simula un login admin y verifica que el container se cree."""
        self.manager.usuario_rol = "admin"
        self.manager.usuario = "admin_user"
        self.manager.cargar_container()

        self.assertIn("Container", self.manager.frames)
        container = self.manager.frames["Container"]
        # Verificar que el Container tiene atributo frames
        self.assertTrue(hasattr(container, "frames"))
        # Verificar que frame de AdminUsuarios se creó
        self.assertIn("AdminUsuarios", container.frames)
    
    def test_logout_resets_session(self):
        """Verifica que logout limpie sesión y destruya container."""
        self.manager.usuario_rol = "admin"
        self.manager.usuario = "admin_user"
        self.manager.cargar_container()

        self.manager.logout()

        self.assertIsNone(self.manager.usuario)
        self.assertIsNone(self.manager.usuario_rol)
        self.assertNotIn("Container", self.manager.frames)

if __name__ == "__main__":
    unittest.main()
