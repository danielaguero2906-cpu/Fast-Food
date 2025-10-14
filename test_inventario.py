import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk
import sys
sys.path.append(r"C:\Users\danie\OneDrive\Documentos\Proyecto Fast Food - Git")

from inventario import Inventario

class TestInventario(unittest.TestCase):

    @patch("inventario.conectar_db")
    def test_articulos_combobox(self, mock_conectar_db):
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [("Hamburguesa",), ("Papas",)]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_conectar_db.return_value = mock_conn

        root = tk.Tk()
        inventario = Inventario(root, MagicMock())
        inventario.conectar()
        inventario.comboboxbuscar = ttk.Combobox(root)
        inventario.articulos_combobox()

        valores = list(inventario.comboboxbuscar['values'])
        self.assertIn("Hamburguesa", valores)
        self.assertIn("Papas", valores)
        root.destroy()

    @patch("inventario.conectar_db")
    def test_filtrar_articulos(self, mock_conectar_db):
        root = tk.Tk()
        inventario = Inventario(root, MagicMock())
        inventario.comboboxbuscar = ttk.Combobox(root)
        inventario.articulos = ["Hamburguesa", "Papas"]

        inventario.comboboxbuscar.set("Ham")
        inventario._filter_articulos()

        valores = list(inventario.comboboxbuscar['values'])
        self.assertEqual(valores, ["Hamburguesa"])
        root.destroy()

if __name__ == "__main__":
    unittest.main()

