import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# ---------- Conexión a la BD ----------
def conectar_db():
    """
    Establece la conexión con la base de datos SQL Server.

    Retorna:
        pyodbc.Connection | None: Objeto de conexión a la base de datos si la conexión es exitosa.
                                 En caso de error, retorna None y muestra un mensaje en pantalla.
    """
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=LAPTOP-JKQOT32P\\SQLEXPRESS;"
            "DATABASE=FastFoodDB;"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{e}")
        return None


# ---------- Clase Clientes ----------
class Clientes(tk.Frame):
    """
    Interfaz gráfica para la gestión de clientes dentro del sistema FastFood.

    Permite registrar, modificar, eliminar y visualizar registros de clientes
    almacenados en la base de datos SQL Server.

    Atributos:
        controlador: Referencia al controlador principal del sistema.
        entries (dict): Diccionario que asocia los nombres de los campos con sus Entry correspondientes.
        tre (ttk.Treeview): Tabla que muestra los registros de clientes.
    """
    def __init__(self, parent, controlador):
        """
        Inicializa la ventana de gestión de clientes.

        Args:
            parent (tk.Widget): Ventana o contenedor padre.
            controlador: Controlador principal que maneja la navegación entre ventanas.
        """
        super().__init__(parent, bg="#f7f9fc")
        self.controlador = controlador
        self.estilos()
        self.widgets()
        self.cargar_registros()

    def estilos(self):
        """
        Define los estilos visuales de la interfaz (colores, fuentes y apariencia de los componentes ttk).
        """
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#000000",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 11))
        style.configure("Treeview.Heading",
                        background="#0078D7",
                        foreground="white",
                        font=("Segoe UI Semibold", 12))
        style.map("Treeview", background=[("selected", "#BBDCFB")])

        style.configure("TButton",
                        font=("Segoe UI Semibold", 11),
                        padding=6,
                        background="#0078D7",
                        foreground="white",
                        borderwidth=0)
        style.map("TButton",
                  background=[("active", "#005A9E")])

        style.configure("TLabel", font=("Segoe UI", 11), background="#f7f9fc")

        style.configure("TEntry", padding=4)

    def widgets(self):
        """
        Crea y organiza todos los elementos gráficos (labels, entries, botones y tablas)
        que componen la interfaz de gestión de clientes.
        """
        # ---- PANEL IZQUIERDO ----
        contenedor_panel = tk.Canvas(self, bg="#f7f9fc", highlightthickness=0)
        contenedor_panel.place(x=30, y=30, width=310, height=540)

        scroll_y = ttk.Scrollbar(self, orient="vertical", command=contenedor_panel.yview)
        scroll_y.place(x=330, y=30, height=540)
        contenedor_panel.configure(yscrollcommand=scroll_y.set)

        panel = tk.Frame(contenedor_panel, bg="#ffffff", bd=1, relief="solid")
        contenedor_panel.create_window((0, 0), window=panel, anchor="nw", width=310)

        panel.bind("<Configure>", lambda e: contenedor_panel.configure(scrollregion=contenedor_panel.bbox("all")))

        # --- Título ---
        tk.Label(panel, text="Gestión de Clientes",
                font=("Segoe UI Semibold", 16), bg="#ffffff", fg="#333").pack(pady=20)

        # --- Campos de texto ---
        campos = [
            ("Nombre", "nombre"),
            ("Cédula", "cedula"),
            ("Celular", "celular"),
            ("Dirección", "direccion"),
            ("Correo", "correo"),
        ]

        self.entries = {}
        for texto, var in campos:
            lbl = ttk.Label(panel, text=texto + ":")
            lbl.pack(anchor="w", padx=20, pady=(8, 0))
            entry = ttk.Entry(panel, width=30)
            entry.pack(padx=20, pady=4)
            self.entries[var] = entry

        # --- Botones ---
        ttk.Button(panel, text="Registrar", command=self.registrar).pack(padx=20, pady=(25, 10), fill="x")
        ttk.Button(panel, text="Modificar", command=self.modificar).pack(padx=20, pady=5, fill="x")
        ttk.Button(panel, text="Eliminar Cliente", command=self.eliminar).pack(padx=20, pady=(5, 20), fill="x")

        # ---- TABLA DERECHA ----
        tabla_frame = ttk.LabelFrame(self, text="Lista de Clientes", padding=10)
        tabla_frame.place(x=360, y=30, width=800, height=540)

        columnas = ("ID", "Nombre", "Cedula", "Celular", "Direccion", "Correo")
        self.tre = ttk.Treeview(tabla_frame, columns=columnas, show="headings")

        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28, background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 12), background="#0078D7", foreground="white")

        for col in columnas:
            self.tre.heading(col, text=col)
            ancho = 120 if col not in ("Direccion", "Correo") else 200
            self.tre.column(col, width=ancho, anchor="center")

        vsb = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tre.yview)
        self.tre.configure(yscroll=vsb.set)
        self.tre.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.tre.bind("<Double-1>", self.cargar_campos_desde_tabla)

    # ---------- Funciones de BD ----------
    def valider_campos(self):
        """
        Verifica que todos los campos del formulario estén completos.

        Retorna:
            bool: True si todos los campos están completos, False en caso contrario.
        """
        for entry in self.entries.values():
            if not entry.get().strip():
                messagebox.showerror("Error", "Todos los campos son requeridos.")
                return False
        return True

    def registrar(self):
        """
        Inserta un nuevo registro de cliente en la base de datos
        utilizando los valores de los campos del formulario.
        """
        if not self.valider_campos():
            return
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nombre, cedula, celular, direccion, correo)
                VALUES (?, ?, ?, ?, ?)
            """, tuple(e.get() for e in self.entries.values()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
            self.limpiar_campos()
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente:\n{e}")

    def cargar_registros(self):
        """
        Carga todos los clientes almacenados en la base de datos y los muestra en la tabla.
        """
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, cedula, celular, direccion, correo FROM clientes ORDER BY id ASC")
            rows = cursor.fetchall()
            self.limpiar_treeview()
            
            for row in rows:
                valores = [str(col).strip().replace("'", "") for col in row]
                self.tre.insert("", "end", values=valores)
                
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes:\n{e}")

    def limpiar_treeview(self):
        """Elimina todos los elementos actuales del Treeview."""
        for item in self.tre.get_children():
            self.tre.delete(item)

    def limpiar_campos(self):
        """Limpia los campos de entrada del formulario."""
        for e in self.entries.values():
            e.delete(0, tk.END)

    def cargar_campos_desde_tabla(self, event):
        """
        Carga los datos del cliente seleccionado desde la tabla hacia los campos del formulario.

        Args:
            event: Evento de doble clic sobre la tabla.
        """
        item = self.tre.focus()
        if not item:
            return
        valores = self.tre.item(item, "values")
        for key, val in zip(self.entries.keys(), valores[1:]):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, val)

    def modificar(self):
        """
        Modifica la información de un cliente existente en la base de datos
        con los valores actuales de los campos del formulario.
        """
        item = self.tre.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un cliente para modificar.")
            return

        id_cliente = self.tre.item(item, "values")[0]
        valores = [e.get() for e in self.entries.values()]

        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes
                SET nombre=?, cedula=?, celular=?, direccion=?, correo=?
                WHERE id=?
            """, (*valores, id_cliente))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cliente modificado correctamente.")
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el cliente:\n{e}")

    def eliminar(self):
        """
        Elimina un cliente seleccionado de la base de datos, previa confirmación del usuario.
        Si la tabla queda vacía, reinicia el contador de identidad (ID) a 0.
        """
        item = self.tre.focus()
        if not item:
            messagebox.showerror("Error", "Seleccione un cliente para eliminar.")
            return

        valores = self.tre.item(item, "values")
        id_cliente = valores[0]
        nombre_cliente = valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"Esta seguro de eliminar al cliente '{nombre_cliente}'?\nEsta accion no se puede deshacer."
        )

        if not confirmar:
            return

        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM clientes")
            total = cursor.fetchone()[0]
            if total == 0:
                cursor.execute("DBCC CHECKIDENT ('clientes', RESEED, 0)")
                conn.commit()
            
            conn.close()

            messagebox.showwarning("Eliminado", f"El cliente '{nombre_cliente}' ha sido eliminado.")
            self.cargar_registros()
            
            self.cargar_registros()
            self.master.event_generate("<<ClienteEliminado>>", when="tail")
            

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente:\n{e}")
            
         
        