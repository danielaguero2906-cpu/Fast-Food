import pyodbc
from tkinter import *   
import tkinter as tk  
from tkinter import ttk
from tkinter import messagebox
from container import Container

def conectar_db():
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
class Login(tk.Frame):
    
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.config(bg="#f0f4f7")
        self.create_widgets()
        
    def create_widgets(self):
        
        container = tk.Frame(self, bg="#f0f4f7")
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(container, text="Iniciar Sesión", font=("Helvetica", 20, "bold"), bg="#f0f4f7", fg="#333")
        title.pack(pady=(40, 20))

        form_frame = tk.Frame(container, bg="#f0f4f7")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Usuario:", font=("Helvetica", 12), bg="#f0f4f7").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_usuario = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.entry_usuario.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(form_frame, text="Contraseña:", font=("Helvetica", 12), bg="#f0f4f7").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_password = tk.Entry(form_frame, font=("Helvetica", 12), width=30, show="*")
        self.entry_password.grid(row=1, column=1, pady=5, padx=10)

        btn_login = tk.Button(container, text="Iniciar Sesión", font=("Helvetica", 14), bg="#4a90e2", fg="white",
                              activebackground="#357ABD", activeforeground="white", command=self.login)
        btn_login.pack(pady=(20, 10), ipadx=10, ipady=5)

        btn_registro = tk.Button(container, text="Registrarse", font=("Helvetica", 12), bg="#e1e5ea", fg="#333",
                                 activebackground="#c1c7d0", activeforeground="#333", command=self.ir_registro)
        btn_registro.pack()
        
    def login(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        
        if usuario == "" or password == "":
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa usuario y contraseña.")
            return
        
        conn = conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM usuarios WHERE usuario = ? AND password = ?"
            cursor.execute(query, (usuario, password))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] == 1:
                messagebox.showinfo("Login exitoso", f"Bienvenido {usuario}!")
                self.controlador.show_frame(Container)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos:\n{e}")
        finally:
            conn.close()
                
    def ir_registro(self):
        self.controlador.show_frame(Registro)
        
class Registro(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent)
        self.controlador = controlador
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.config(bg="#f0f4f7")
        self.create_widgets()    
        
    def create_widgets(self):
        title = tk.Label(self, text="Registro de Usuario", font=("Helvetica", 20, "bold"), bg="#f0f4f7", fg="#333")
        title.pack(pady=(40, 20))
        
        form_frame = tk.Frame(self, bg="#f0f4f7")
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Usuario:", font=("Helvetica", 12), bg="#f0f4f7").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_usuario = tk.Entry(form_frame, font=("Helvetica", 12), width=30)
        self.entry_usuario.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Contraseña:", font=("Helvetica", 12), bg="#f0f4f7").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_password = tk.Entry(form_frame, font=("Helvetica", 12), width=30, show="*")
        self.entry_password.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Confirmar Contraseña:", font=("Helvetica", 12), bg="#f0f4f7").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_password_confirm = tk.Entry(form_frame, font=("Helvetica", 12), width=30, show="*")
        self.entry_password_confirm.grid(row=2, column=1, pady=5, padx=10)

        btn_registrar = tk.Button(self, text="Registrar", font=("Helvetica", 14), bg="#4a90e2", fg="white",
                                   activebackground="#357ABD", activeforeground="white", command=self.registrar)
        btn_registrar.pack(pady=(20, 10), ipadx=10, ipady=5)

        btn_volver = tk.Button(self, text="Volver al Login", font=("Helvetica", 12), bg="#e1e5ea", fg="#333",
                               activebackground="#c1c7d0", activeforeground="#333", command=self.ir_login)
        btn_volver.pack()
        
    def registrar(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        password_confirm = self.entry_password_confirm.get()
        if not usuario or not password or not password_confirm:
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            return
        if password != password_confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        conn = conectar_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "El usuario ya existe.")
                return

            cursor.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (usuario, password))
            conn.commit()
            messagebox.showinfo("Registro exitoso", f"Usuario {usuario} registrado correctamente.")
            self.ir_login()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")
        finally:
            conn.close()
            
    def ir_login(self):
        self.controlador.show_frame(Login)