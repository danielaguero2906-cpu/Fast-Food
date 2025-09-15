import unittest
from unittest.mock import MagicMock, patch
import bcrypt
from login import hash_password, verify_password, UsuarioDAO, autenticar_usuario


class TestPasswordUtils(unittest.TestCase):

    def test_hash_and_verify_password(self):
        password = "miClaveSegura123"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("otraClave", hashed))


class TestUsuarioDAO(unittest.TestCase):

    def setUp(self):
        # Mock de conexión y cursor
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.cursor.return_value = self.cursor
        self.dao = UsuarioDAO(self.conn)

    def test_crear_usuario_existe(self):
        self.cursor.fetchone.return_value = [1]  # usuario ya existe
        with self.assertRaises(ValueError):
            self.dao.crear_usuario("usuario1", "1234")

    def test_crear_usuario_ok(self):
        self.cursor.fetchone.return_value = [0]  # no existe
        self.dao.crear_usuario("usuario1", "1234", "usuario")
        self.conn.commit.assert_called_once()

    def test_modificar_usuario_sin_campos(self):
        with self.assertRaises(ValueError):
            self.dao.modificar_usuario(1)  # sin parámetros

    def test_modificar_usuario_ok(self):
        self.dao.modificar_usuario(1, nuevo_usuario="nuevo")
        self.conn.commit.assert_called_once()

    def test_asignar_y_borrar_usuario(self):
        self.dao.asignar_rol(1, "admin")
        self.dao.borrar_usuario(1)
        self.conn.commit.assert_called()


class TestAutenticacion(unittest.TestCase):

    def setUp(self):
        self.conn = MagicMock()
        self.cursor = MagicMock()
        self.conn.cursor.return_value = self.cursor

    def test_autenticar_usuario_valido(self):
        # Simula que en la BD está el hash correcto
        password = "clave123"
        hashed = hash_password(password)
        self.cursor.fetchone.return_value = [(hashed, "admin")]
        with patch("login.verify_password", return_value=True):
            rol = autenticar_usuario(self.conn, "usuario1", password)
            self.assertEqual(rol, "admin")

    def test_autenticar_usuario_invalido(self):
        self.cursor.fetchone.return_value = None
        rol = autenticar_usuario(self.conn, "noexiste", "123")
        self.assertIsNone(rol)


if __name__ == "__main__":
    unittest.main()
