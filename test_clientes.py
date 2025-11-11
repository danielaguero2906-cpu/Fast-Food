import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk

from clientes import Clientes 


class TestClientes(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.frame = Clientes(self.root, controlador=None)

    def tearDown(self):
        self.root.destroy()

    def test_validar_campos_incompletos(self):
        """Debe mostrar error si algún campo está vacío."""
        for entry in self.frame.entries.values():
            entry.delete(0, tk.END)
        with patch("clientes.messagebox.showerror") as mock_error:
            resultado = self.frame.valider_campos()
            self.assertFalse(resultado)
            mock_error.assert_called_once()

    def test_validar_campos_completos(self):
        """Debe devolver True si todos los campos están llenos."""
        for entry in self.frame.entries.values():
            entry.insert(0, "dato")
        self.assertTrue(self.frame.valider_campos())

    @patch("clientes.conectar_db")
    def test_registrar_cliente(self, mock_conectar_db):
        """Debe insertar un nuevo cliente correctamente."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        for entry in self.frame.entries.values():
            entry.insert(0, "dato")

        with patch("clientes.messagebox.showinfo") as mock_info:
            self.frame.registrar()
            # Verifica que se haya ejecutado al menos una vez el INSERT
            found = any("INSERT INTO clientes" in str(call.args[0]) for call in mock_cursor.execute.call_args_list)
            self.assertTrue(found, "No se encontró la consulta INSERT.")
            mock_conn.commit.assert_called()
            mock_info.assert_called_once_with("Éxito", "Cliente registrado correctamente.")



    @patch("clientes.conectar_db")
    def test_cargar_registros(self, mock_conectar_db):
        """Debe cargar registros en el Treeview desde la base de datos."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Juan", "123", "999", "Calle X", "juan@mail.com"),
            (2, "Ana", "124", "888", "Calle Y", "ana@mail.com")
        ]
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        self.frame.cargar_registros()

        items = self.frame.tre.get_children()
        self.assertEqual(len(items), 2)

    @patch("clientes.conectar_db")
    def test_modificar_cliente(self, mock_conectar_db):
        """Debe modificar cliente seleccionado correctamente."""
        self.frame.tre.insert("", "end", values=(1, "Juan", "123", "999", "Dir", "correo"))
        self.frame.tre.selection_set(self.frame.tre.get_children()[0])
        self.frame.tre.focus(self.frame.tre.get_children()[0])

        for entry in self.frame.entries.values():
            entry.insert(0, "Nuevo valor")

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        with patch("clientes.messagebox.showinfo") as mock_info:
            self.frame.modificar()
            found = any("UPDATE clientes" in str(call.args[0]) for call in mock_cursor.execute.call_args_list)
            self.assertTrue(found, "No se encontró la consulta UPDATE.")
            mock_conn.commit.assert_called()
            mock_info.assert_called_once_with("Éxito", "Cliente modificado correctamente.")


    @patch("clientes.conectar_db")
    def test_eliminar_cliente(self, mock_conectar_db):
        """Debe eliminar un cliente seleccionado con confirmación."""
        self.frame.tre.insert("", "end", values=(1, "Pedro", "123", "999", "Dir", "correo"))
        self.frame.tre.focus(self.frame.tre.get_children()[0])

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conectar_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        with patch("clientes.messagebox.askyesno", return_value=True), \
             patch("clientes.messagebox.showwarning") as mock_warn:
            self.frame.eliminar()
            mock_cursor.execute.assert_any_call("DELETE FROM clientes WHERE id=?", ('1',))
            mock_conn.commit.assert_called()
            mock_warn.assert_called_once()


if __name__ == "__main__":
    unittest.main()
