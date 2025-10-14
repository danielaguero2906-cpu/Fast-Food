import bcrypt
import pyodbc
import tkinter as tk
from tkinter import messagebox, simpledialog
from inventario import Inventario
from PIL import Image, ImageTk  

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
    
    
# ---------- Scripts para funcion de encriptacion de contraseñas  ----------
def hash_password(password: str) -> str:
    """
    Genera un hash seguro para una contraseña usando bcrypt.

    Args:
        password (str): Contraseña en texto plano.

    Returns:
        str: Contraseña hasheada.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8') 

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con un hash almacenado.

    Args:
        password (str): Contraseña en texto plano.
        hashed (str): Hash de la contraseña almacenado en la BD.

    Returns:
        bool: True si coincide, False en caso contrario.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


    #Diseño de la interfaz
class RoundedEntry(tk.Frame):
    """
    Entrada de texto personalizada con esquinas redondeadas y placeholder.
    
    Attributes:
        placeholder (str): Texto que aparece cuando no hay input.
        is_password (bool): Indica si la entrada es de tipo contraseña.
    """
    def __init__(self, parent, placeholder="", is_password=False, width_px=360, height_px=44, radius=20):
        """
        Inicializa la entrada redondeada.

        Args:
            parent (tk.Widget): Widget padre.
            placeholder (str): Texto placeholder.
            is_password (bool): Mostrar caracteres ocultos.
            width_px (int): Ancho del widget.
            height_px (int): Alto del widget.
            radius (int): Radio de las esquinas.
        """
        super().__init__(parent, bg="#ffffff")
        self.placeholder = placeholder
        self.is_password = is_password
        self._has_placeholder = True
        self.width_px = width_px
        self.height_px = height_px
        self.radius = radius
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=0,
                                 width=self.width_px, height=self.height_px)
        self.canvas.pack()
        self._draw_rounded_rect()
        self.entry = tk.Entry(self, bd=0, bg="#ecf0f1", font=("Segoe UI", 11))
        self.entry.place(x=12, y=10, width=self.width_px - 24, height=self.height_px - 20)
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg="#7f8c8d", show="")
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _draw_rounded_rect(self):
        x1, y1 = 2, 2
        x2, y2 = self.width_px - 2, self.height_px - 2
        r = self.radius
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1,
        ]
        self.canvas.create_polygon(points, smooth=True, fill="#ecf0f1", outline="")

    def _on_focus_in(self, _):
        if self._has_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg="#2c3e50")
            if self.is_password:
                self.entry.config(show="*")
            self._has_placeholder = False

    def _on_focus_out(self, _):
        if not self.entry.get():
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg="#7f8c8d", show="")
            self._has_placeholder = True

    def get(self):
        """
        Obtiene el valor actual de la entrada.

        Returns:
            str: Valor de la entrada o vacío si es el placeholder.
        """
        return "" if self._has_placeholder else self.entry.get()

    def clear(self):
        self.entry.delete(0, tk.END)
        self._on_focus_out(None)


# ---------- Asignación de Roles----------
class UsuarioDAO:
    """
    Data Access Object para operaciones de usuarios en la base de datos.
    """
    def __init__(self, conn):
        self.conn = conn

    def consultar_usuarios(self):
        """
        Consulta todos los usuarios registrados.

        Returns:
            list: Lista de tuplas con (id, usuario, rol)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, usuario, rol FROM usuarios")
        return cursor.fetchall()

    def crear_usuario(self, usuario, password, rol='usuario'):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone()[0] > 0:
            raise ValueError("El usuario ya existe")
        hashed = hash_password(password)
        cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", (usuario, hashed, rol))
        self.conn.commit()

    def modificar_usuario(self, usuario_id, nuevo_usuario=None, nuevo_password=None, nuevo_rol=None):
        cursor = self.conn.cursor()
        campos = []
        valores = []
        if nuevo_usuario:
            campos.append("usuario = ?")
            valores.append(nuevo_usuario)
        if nuevo_password:
            campos.append("password = ?")
            valores.append(hash_password(nuevo_password))
        if nuevo_rol:
            campos.append("rol = ?")
            valores.append(nuevo_rol)
        if not campos:
            raise ValueError("No se especificaron campos para modificar")
        valores.append(usuario_id)
        sql = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(sql, valores)
        self.conn.commit()

    def asignar_rol(self, usuario_id, rol):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (rol, usuario_id))
        self.conn.commit()

    def borrar_usuario(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        self.conn.commit() 
        
# ---------- Login ----------
class Login(tk.Frame):
    """
    Frame de inicio de sesión.
    
    Permite al usuario autenticarse y cargar el módulo correspondiente según su rol.
    """
    def __init__(self, parent, controlador):
        super().__init__(parent, bg="#f5f6fa")
        self.controlador = controlador
        self.place(x=0, y=0, width=1100, height=650)
        self._build()

    def _build(self):
        card = tk.Frame(self, bg="#ffffff")
        card.place(relx=0.5, rely=0.5, anchor="center", width=560, height=460)
        tk.Label(card, text="Iniciar Sesión", font=("Segoe UI", 26, "bold"),
                 bg="#ffffff", fg="#2f3640").pack(pady=(32, 18))
        form = tk.Frame(card, bg="#ffffff")
        form.pack()
        self.user_input = RoundedEntry(form, placeholder="Usuario", width_px=420)
        self.user_input.pack(pady=10)
        self.pass_input = RoundedEntry(form, placeholder="Contraseña", is_password=True, width_px=420)
        self.pass_input.pack(pady=10)
        tk.Button(card, text="Ingresar",
                  font=("Segoe UI", 12, "bold"),
                  bg="#0984e3", fg="white",
                  command=self.login).pack(pady=(26, 8))

        sep = tk.Frame(card, bg="#eef2f5", height=2)
        sep.pack(fill="x", padx=40, pady=8)
        tk.Button(card, text="Crear nuevo Usuario",
                  font=("Segoe UI", 12,"bold"),
                  bg="#0984e3", fg="white",
                  command=self.ir_registro).pack(pady=6)

    def login(self):
        """
        Verifica las credenciales ingresadas y autentica al usuario.

        Muestra mensajes de error si los datos son incorrectos o la BD no responde.
        """
        usuario = self.user_input.get()
        password = self.pass_input.get()
        if not usuario or not password:
            messagebox.showwarning("Campos vacíos", "Por favor, ingresa usuario y contraseña.")
            return
        conn = conectar_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, password, rol FROM usuarios WHERE usuario = ?", (usuario,))
            row = cursor.fetchone()
            if row:
                user_id, stored_pass, rol = row
                
                if stored_pass.startswith("$2b$") and verify_password(password, stored_pass):
                    self.controlador.usuario = usuario
                    self.controlador.usuario_rol = rol.strip().lower()
                    messagebox.showinfo("Login exitoso", f"¡Bienvenido {usuario}!")
                    self.controlador.cargar_container()

                elif password == stored_pass:
                    new_hash = hash_password(password)
                    cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (new_hash, user_id))
                    conn.commit()
                    self.controlador.usuario = usuario
                    self.controlador.usuario_rol = rol.strip().lower()
                    messagebox.showinfo("Login exitoso", f"¡Bienvenido {usuario}!")
                    self.controlador.cargar_container()
                
                else:
                   messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos:\n{e}")
        finally:
            conn.close()

    def ir_registro(self):
        self.controlador.show_frame("Registro")
        
# Registro 
class Registro(tk.Frame):
    """
        Permite a un nuevo usuario registrarse en el sistema.

        Muestra mensajes de error si los datos son incorrectos o la BD no responde.
        """
    def __init__(self, parent, controlador):
        """
        Inicializa el formulario de registro.
        """
        super().__init__(parent, bg="#f5f6fa")
        self.controlador = controlador
        self.place(x=0, y=0, width=1100, height=650)
        self._build()

    def _build(self):
        """
        Construye la interfaz gráfica del formulario de registro.
        """
        card = tk.Frame(self, bg="#ffffff")
        card.place(relx=0.5, rely=0.5, anchor="center", width=620, height=520)
        tk.Label(card, text="Registro de Usuario", font=("Segoe UI", 26, "bold"),
                 bg="#ffffff", fg="#2f3640").pack(pady=(32, 18))
        form = tk.Frame(card, bg="#ffffff")
        form.pack()
        self.user_input = RoundedEntry(form, placeholder="Usuario", width_px=460)
        self.user_input.pack(pady=10)
        self.pass_input = RoundedEntry(form, placeholder="Contraseña", is_password=True, width_px=460)
        self.pass_input.pack(pady=10)
        self.pass2_input = RoundedEntry(form, placeholder="Confirmar contraseña", is_password=True, width_px=460)
        self.pass2_input.pack(pady=10)

        tk.Button(card, text="Registrar",
                  font=("Segoe UI", 12, "bold"),
                  bg="#27ae60", fg="white",
                  command=self.registrar).pack(pady=(26, 8))
        sep = tk.Frame(card, bg="#eef2f5", height=2)
        sep.pack(fill="x", padx=40, pady=8)
        tk.Button(card, text="Volver al Login",
                  font=("Segoe UI", 10, "underline"),
                  bg="#ffffff", fg="#0984e3",
                  command=self.ir_login).pack(pady=6)

    def registrar(self):
        """
        Registra un nuevo usuario en la base de datos.
        """
        usuario = self.user_input.get()
        password = self.pass_input.get()
        password2 = self.pass2_input.get()
        if not usuario or not password or not password2:
            messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
            return
        if password != password2:
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
            hashed = hash_password(password)
            cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", (usuario, hashed, 'usuario'))
            conn.commit()
            messagebox.showinfo("Registro exitoso", f"Usuario {usuario} registrado correctamente.")
            self.ir_login()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")
        finally:
            conn.close()

    def ir_login(self):
        self.controlador.show_frame("Login")


# Administración de Usuarios
class AdminUsuarios(tk.Frame):
    def __init__(self, parent, controlador):
        """
        Frame para la administración de usuarios.
        Permite crear, modificar, asignar roles y borrar usuarios.
        """
        super().__init__(parent, bg="#f5f6fa")
        self.controlador = controlador
        self.place(x=0, y=0, width=1100, height=650)
        self.conn = conectar_db()
        if not self.conn:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return
        self.dao = UsuarioDAO(self.conn)
        self._build()

    def _build(self):
        """"Construye la interfaz gráfica del frame de administración de usuarios."""
        tk.Label(self, text="Administrar Usuarios", font=("Segoe UI", 20, "bold"), bg="#f5f6fa").pack(pady=10)
        
        frame_filtro = tk.Frame(self, bg="#f5f6fa")
        frame_filtro.pack(pady=5)
        
        tk.Label(frame_filtro, text="Buscar usuario:", bg="#f5f6fa", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.entry_busqueda = tk.Entry(frame_filtro, width=30)
        self.entry_busqueda.pack(side=tk.LEFT, padx=5)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.filtrar_usuarios())
        
        tk.Button(frame_filtro, text="Buscar", command=self.filtrar_usuarios).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_filtro, text="Limpiar", command=self.cargar_usuarios).pack(side=tk.LEFT, padx=5)

        # --- LISTA DE USUARIOS ---
        self.listbox = tk.Listbox(self, width=70, height=20)
        self.listbox.pack(pady=10)

        # --- BOTONES DE ACCIÓN ---
        frame_btns = tk.Frame(self, bg="#f5f6fa")
        frame_btns.pack(pady=10)

        tk.Button(frame_btns, text="Crear Usuario", command=self.crear_usuario).grid(row=0, column=0, padx=5)
        tk.Button(frame_btns, text="Modificar Usuario", command=self.modificar_usuario).grid(row=0, column=1, padx=5)
        tk.Button(frame_btns, text="Asignar Rol", command=self.asignar_rol).grid(row=0, column=2, padx=5)
        tk.Button(frame_btns, text="Borrar Usuario", command=self.borrar_usuario).grid(row=0, column=3, padx=5)
        tk.Button(frame_btns, text="Actualizar Lista", command=self.cargar_usuarios).grid(row=0, column=4, padx=5)
        tk.Button(frame_btns, text="Cerrar Sesión", command=self.cerrar_sesion).grid(row=0, column=5, padx=5)
        self.cargar_usuarios()
        
    def filtrar_usuarios(self):
        """
        Filtra la lista de usuarios según el texto ingresado en el campo de búsqueda.
        """
        filtro = self.entry_busqueda.get().strip().lower()
        self.listbox.delete(0, tk.END)
        try:
            usuarios = self.dao.consultar_usuarios()
            usuarios_filtrados = [u for u in usuarios if filtro in u[1].lower()]
            for u in usuarios_filtrados:
                self.listbox.insert(tk.END, f"{u[0]} - {u[1]} - {u[2]}")
            if not usuarios_filtrados:
                self.listbox.insert(tk.END, "No se encontraron usuarios.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar el filtro:\n{e}")

    def cargar_usuarios(self):
        """
        Carga todos los usuarios desde la base de datos y los muestra en la lista.
        """
        self.listbox.delete(0, tk.END)
        try:
            usuarios = self.dao.consultar_usuarios()
            for u in usuarios:
                self.listbox.insert(tk.END, f"{u[0]} - {u[1]} - {u[2]}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar usuarios:\n{e}")

    def obtener_usuario_seleccionado(self):
        """
        Obtiene el ID del usuario seleccionado en la lista.
        """
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un usuario primero")
            return None
        texto = self.listbox.get(seleccion[0])
        return int(texto.split(" - ")[0])

    def crear_usuario(self):
        """
        Crea un nuevo usuario solicitando datos mediante diálogos.
        """
        usuario = simpledialog.askstring("Crear Usuario", "Nombre de usuario:")
        if not usuario:
            return
        password = simpledialog.askstring("Crear Usuario", "Contraseña:", show="*")
        if not password:
            return
        rol = simpledialog.askstring("Crear Usuario", "Rol (por defecto 'usuario'):", initialvalue="usuario")
        if not rol:
            rol = "usuario"
        try:
            self.dao.crear_usuario(usuario, password, rol)
            messagebox.showinfo("Éxito", f"Usuario '{usuario}' creado.")
            self.cargar_usuarios()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear usuario:\n{e}")

    def modificar_usuario(self):
        """
        Modifica los datos de un usuario seleccionado.
        Solicita nuevos datos mediante diálogos.
        """
        usuario_id = self.obtener_usuario_seleccionado()
        if usuario_id is None:
            return
        nuevo_usuario = simpledialog.askstring("Modificar Usuario", "Nuevo nombre de usuario (dejar vacío para no cambiar):")
        nuevo_password = simpledialog.askstring("Modificar Usuario", "Nueva contraseña (dejar vacío para no cambiar):", show="*")
        nuevo_rol = simpledialog.askstring("Modificar Usuario", "Nuevo rol (dejar vacío para no cambiar):")
        if not (nuevo_usuario or nuevo_password or nuevo_rol):
            messagebox.showinfo("Info", "No se modificó ningún campo.")
            return
        try:
            self.dao.modificar_usuario(usuario_id, nuevo_usuario or None, nuevo_password or None, nuevo_rol or None)
            messagebox.showinfo("Éxito", "Usuario modificado correctamente.")
            self.cargar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar usuario:\n{e}")

    def asignar_rol(self):
        """
        Asigna un nuevo rol a un usuario seleccionado.
        Solicita el nuevo rol mediante un diálogo.
        """
        usuario_id = self.obtener_usuario_seleccionado()
        if usuario_id is None:
            return
        rol = simpledialog.askstring("Asignar Rol", "Nuevo rol para el usuario:")
        if not rol:
            messagebox.showinfo("Info", "No se asignó ningún rol.")
            return
        try:
            self.dao.asignar_rol(usuario_id, rol)
            messagebox.showinfo("Éxito", "Rol asignado correctamente.")
            self.cargar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo asignar rol:\n{e}")

    def borrar_usuario(self):
        """
        Borra un usuario seleccionado tras confirmar la acción.
        """
        usuario_id = self.obtener_usuario_seleccionado()
        if usuario_id is None:
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar este usuario?"):
            try:
                self.dao.borrar_usuario(usuario_id)
                messagebox.showinfo("Éxito", "Usuario borrado correctamente.")
                self.cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo borrar usuario:\n{e}")

    def cerrar_sesion(self):
        self.controlador.logout()
        
    def __del__(self):
        if self.conn:
            self.conn.close()
            

# Lógica independiente de autenticación

def autenticar_usuario(conn, usuario, password):
    """
    Retorna el rol del usuario si las credenciales son correctas.
    Si no existe, retorna None.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT rol FROM usuarios WHERE usuario = ? AND password = ?",
        (usuario,)
    )
    row = cursor.fetchone()
    if row:
        stored_hash, rol = row[0]
        if verify_password(password, stored_hash):
            return rol.strip().lower()
    return None


    