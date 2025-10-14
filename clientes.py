from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# ---------- Conexión a la BD ----------
def conectar_db():
    """
    Intenta establecer una conexión con la base de datos SQL Server.

    Returns:
        pyodbc.Connection: Conexión a la base de datos si es exitosa.
        None: Si ocurre algún error al conectarse.
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
    
    
class Clientes(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.config(bg="#FFFFFF")
        self.controlador = controlador
        self.widgets()
        self.cargar_registros()

    def widgets(self):
        self.labelframe = tk.LabelFrame(self, text="Clientes", font= "sans 20 bold", bg= "#C6D9E3" ) 
        self.labelframe.place(x=20, y=20, width=250, height=560)
        
        lblnombre = tk.Label(self.labelframe, text="Nombre: ", font="sans 14 bold", bg="#C6D9E3")
        lblnombre.place(x=10, y=20)
        self.nombre = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.nombre.place(x=10, y=50, width=220, height=40)
        
        lblcedula = tk.Label(self.labelframe, text="Cedula: ", font="sans 14 bold", bg="#C6D9E3")
        lblcedula.place(x=10, y=100)
        self.cedula = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.cedula.place(x=10, y=130, width=220, height=40)
        
        lblcelular = tk.Label(self.labelframe, text="Celular: ", font="sans 14 bold", bg="#C6D9E3")
        lblcelular.place(x=10, y=180)
        self.celular = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.celular.place(x=10, y=210, width=220, height=40)
        
        lbldireccion = tk.Label(self.labelframe, text="Direccion: ", font="sans 14 bold", bg="#C6D9E3")
        lbldireccion.place(x=10, y=260)
        self.direccion = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.direccion.place(x=10, y=290, width=220, height=40)
        
        lblcorreo = tk.Label(self.labelframe, text="Correo: ", font="sans 14 bold", bg="#C6D9E3")
        lblcorreo.place(x=10, y=340)
        self.correo = ttk.Entry(self.labelframe, font="sans 14 bold")
        self.correo.place(x=10, y=370, width=220, height=40)
        
        btn1 = Button(self.labelframe, fg="Black", text="Ingresar", font="sans 16 bold", command=self.registrar)
        btn1.place(x=10, y=420, width=220, height=40)
        
        btn2 = Button(self.labelframe, fg="Black", text="Modificar", font="sans 16 bold", command=self.modificar)
        btn2.place(x=10, y=470, width=220, height=40)
        
        treFrame = Frame(self, bg="white")
        treFrame.place(x=280, y=20, width=800, height=560)
        
        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side= RIGHT, fill=Y)
        
        scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
        scrol_x.pack(side=BOTTOM, fill=X)
        
        self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, height=40
                                , columns=("ID", "Nombre", "Cedula", "Celular", "Direccion", "Correo"), show="headings")
        
        self.tre.pack(expand=True, fill=BOTH)
        
        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)
        
        self.tre.heading("ID", text="ID")
        self.tre.heading("Nombre", text="Nombre")
        self.tre.heading("Cedula", text="Cedula")
        self.tre.heading("Celular", text="Celular")
        self.tre.heading("Direccion", text="Direccion")
        self.tre.heading("Correo", text="Correo")
        
        self.tre.column("ID", width=50, anchor="center")
        self.tre.column("Nombre", width=150, anchor="center")
        self.tre.column("Cedula", width=120, anchor="center")
        self.tre.column("Celular", width=120, anchor="center")
        self.tre.column("Direccion", width=200, anchor="center")
        self.tre.column("Correo", width=200, anchor="center")
        self.tre.bind("<Double-1>", self.cargar_campos_desde_tabla)
        
    def cargar_campos_desde_tabla(self, event):
        item = self.tre.focus()
        if not item:
            return
        
        datos = self.tre.item(item, "values")
        if len(datos) < 6:
            return

        # Cargar los datos en los Entry
        self.nombre.delete(0, END)
        self.nombre.insert(0, datos[1])

        self.cedula.delete(0, END)
        self.cedula.insert(0, datos[2])

        self.celular.delete(0, END)
        self.celular.insert(0, datos[3])

        self.direccion.delete(0, END)
        self.direccion.insert(0, datos[4])

        self.correo.delete(0, END)
        self.correo.insert(0, datos[5])

        
    def valider_campos(self):
        if not self.nombre.get() or not self.cedula.get() or not self.celular.get() or not self.direccion.get() or not self.correo.get():
           messagebox.showerror("Error", "Todos los campos son requeridos")
           return False
        return True
    
    def registrar(self): 
        if not self.valider_campos():
            return
        
        nombre = self.nombre.get()
        cedula = self.cedula.get()
        celular = self.celular.get()
        direccion = self.direccion.get()
        correo = self.correo.get()
        
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clientes (nombre, cedula, celular, direccion, correo) VALUES (?,?,?,?,?)",
                           (nombre, cedula, celular, direccion, correo))
            conn.commit()
            conn.close()
            messagebox.showinfo("Exito", "Cliente registrado correctamente.")
            self.limpiar_campos()
            self.limpiar_treeview()
            self.cargar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el cliente: {e}")
            
    def cargar_registros(self):
        try:
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, cedula, celular, direccion, correo
                FROM clientes
                ORDER BY id ASC
            """)
            rows = cursor.fetchall()
            self.limpiar_treeview()
            
            for row in rows:
                valores = tuple(str(c).strip().replace("[", "").replace("]", "").replace("'", "") for c in row)
                self.tre.insert("", "end", values=valores)
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los registros: {e}")
            
    def limpiar_treeview(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
            
    def limpiar_campos(self):
        self.nombre.delete(0, END)
        self.cedula.delete(0, END)
        self.celular.delete(0, END)
        self.direccion.delete(0, END)
        self.correo.delete(0, END)
            
    def modificar(self):
        if not self.tre.selection():
            messagebox.showerror("Error", "Porfavor seleccione un cliente para modificar.")
            return
        
        item = self.tre.selection()[0]
        id_cliente_str = str(self.tre.item(item, "values")[0]).strip()
        id_cliente = int(''.join(ch for ch in id_cliente_str if ch.isdigit()))
    
        nombre_actual = self.tre.item(item, "values")[1]
        cedula_actual = self.tre.item(item, "values")[2]
        celular_actual = self.tre.item(item, "values")[3]    
        direccion_actual = self.tre.item(item, "values")[4]
        correo_actual = self.tre.item(item, "values")[5]    
        
        top_modificar = Toplevel(self)   
        top_modificar.title("Modificar Cliente")
        top_modificar.geometry("400x400+400+50")
        top_modificar.config(bg="#C6D9E3")
        top_modificar.resizable(False, False)
        top_modificar.transient(self.master)
        top_modificar.grab_set()
        top_modificar.focus_set()
        top_modificar.lift()
        
        tk.Label(top_modificar, text="Nombre: ", font="sans 14 bold", bg="#C6D9E3").grid(row=0, column=0, padx=10, pady=5)
        nombre_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        nombre_nuevo.insert(0, nombre_actual)
        nombre_nuevo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Cedula: ", font="sans 14 bold", bg="#C6D9E3").grid(row=1, column=0, padx=10, pady=5)
        cedula_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        cedula_nuevo.insert(0, cedula_actual)
        cedula_nuevo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Celular: ", font="sans 14 bold", bg="#C6D9E3").grid(row=2, column=0, padx=10, pady=5)
        celular_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        celular_nuevo.insert(0, celular_actual)
        celular_nuevo.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Direccion: ", font="sans 14 bold", bg="#C6D9E3").grid(row=3, column=0, padx=10, pady=5)
        direccion_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        direccion_nuevo.insert(0, direccion_actual)
        direccion_nuevo.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(top_modificar, text="Correo: ", font="sans 14 bold", bg="#C6D9E3").grid(row=4, column=0, padx=10, pady=5)
        correo_nuevo = tk.Entry(top_modificar, font="sans 14 bold")
        correo_nuevo.insert(0, correo_actual)
        correo_nuevo.grid(row=4, column=1, padx=10, pady=5)
        
        def guardar_modificaciones():
            nuevo_nombre = nombre_nuevo.get()
            nueva_cedula = cedula_nuevo.get()
            nuevo_celular = celular_nuevo.get()
            nueva_direccion = direccion_nuevo.get()
            nuevo_correo = correo_nuevo.get()
            
            try:
                conn = conectar_db()
                cursor = conn.cursor()
                cursor.execute("""UPDATE clientes SET nombre =?, cedula = ?, celular =?, direccion = ?, correo = ? WHERE id = ?"""
                               , (nuevo_nombre, nueva_cedula, nuevo_celular, nueva_direccion, nuevo_correo, id_cliente))
                conn.commit()
                conn.close()
                messagebox.showinfo("Exito", "Cliente modificado correctamente")
                self.limpiar_treeview()
                self.cargar_registros()
                top_modificar.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo modificar el cliente: {e}")
                
        btn_guardar = tk.Button(top_modificar, text="Guardar Cambios", command=guardar_modificaciones, font= "sans 14 bold")
        btn_guardar.grid(row=5, column=0, columnspan=2, pady=20)       
            
         
        