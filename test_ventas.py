import unittest
from unittest.mock import MagicMock, patch
from Ventas import Ventas

class TestVentas(unittest.TestCase):

    @patch("Ventas.conectar_db")  # Mockeamos la conexión a la DB
    def test_cargar_clientes(self, mock_conectar_db):
        # Simulamos retorno de la DB
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("Juan",), ("Ana",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_conectar_db.return_value = mock_conn

        # Creamos frame de ventas (sin ventana real)
        ventas_frame = Ventas(MagicMock(), MagicMock())

        # Reemplazamos Combobox por un mock
        ventas_frame.entry_cliente = MagicMock()
        ventas_frame.entry_cliente.__setitem__ = MagicMock()

        # Ejecutamos cargar clientes
        ventas_frame.cargar_clientes()

        # Verificamos que se actualizó el Combobox correctamente
        ventas_frame.entry_cliente.__setitem__.assert_called_with("values", ["Juan", "Ana"])

    @patch("Ventas.conectar_db")  # Mockeamos la conexión a la DB
    def test_cargar_productos(self, mock_conectar_db):
        # Simulamos retorno de la DB
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("Hamburguesa",), ("Papas",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_conectar_db.return_value = mock_conn

        # Creamos frame de ventas
        ventas_frame = Ventas(MagicMock(), MagicMock())

        # Reemplazamos Combobox por un mock
        ventas_frame.entry_producto = MagicMock()
        ventas_frame.entry_producto.__setitem__ = MagicMock()

        # Ejecutamos cargar productos
        ventas_frame.cargar_productos()

        # Verificamos que se actualizó el Combobox correctamente
        ventas_frame.entry_producto.__setitem__.assert_called_with("values", ["Hamburguesa", "Papas"])


if __name__ == "__main__":
    unittest.main()
