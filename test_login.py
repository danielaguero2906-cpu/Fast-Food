import unittest
import login  # importamos el módulo completo

class TestLogin(unittest.TestCase):

    def setUp(self):
        # Se ejecuta antes de cada test
        self.conn = login.conectar_db()
        self.assertIsNotNone(self.conn, "No se pudo conectar a la base de datos")

    def tearDown(self):
        # Se ejecuta después de cada test
        if self.conn:
            self.conn.close()

    def test_login_correcto(self):
        rol = login.autenticar_usuario(self.conn, "admin", "admin")
        self.assertEqual(rol, "admin")

    def test_login_usuario_incorrecto(self):
        rol = login.autenticar_usuario(self.conn, "usuario_falso", "1234")
        self.assertIsNone(rol)

    def test_login_password_incorrecto(self):
        rol = login.autenticar_usuario(self.conn, "admin", "wrong")
        self.assertIsNone(rol)

    def test_login_campos_vacios(self):
        rol = login.autenticar_usuario(self.conn, "", "")
        self.assertIsNone(rol)


if __name__ == "__main__":
    unittest.main()
