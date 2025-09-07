import pyodbc
import tkinter as tk
from tkinter import messagebox, simpledialog

# ---------- Conexión a la BD ----------
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


# ---------- Entrada con borde redondeado ----------
class RoundedEntry(tk.Frame):
    def __init__(self, parent, placeholder="", is_password=False, width_px=360, height_px=44, radius=20):
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
        return "" if self._has_placeholder else self.entry.get()

    def clear(self):
        self.entry.delete(0, tk.END)
        self._on_focus_out(None)


# ---------- DAO Usuarios ----------
class UsuarioDAO:
    def __init__(self, conn):
        self.conn = conn

    def consultar_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, usuario, rol FROM usuarios")
        return cursor.fetchall()

    def crear_usuario(self, usuario, password, rol='usuario'):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone()[0] > 0:
            raise ValueError("El usuario ya existe")
        cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", (usuario, password, rol))
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
            valores.append(nuevo_password)
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

# ---------- Módulos de la app ----------
class Ventas(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent, bg="#dff9fb")
        tk.Label(self, text="Módulo de Ventas", font=("Segoe UI", 20, "bold")).pack(pady=30)
        

class Inventario(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent, bg="#c7ecee")
        tk.Label(self, text="Módulo de Inventario", font=("Segoe UI", 20, "bold")).pack(pady=30)

class Clientes(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent, bg="#fab1a0")
        tk.Label(self, text="Módulo de Clientes", font=("Segoe UI", 20, "bold")).pack(pady=30)
# ---------- Login ----------
class Login(tk.Frame):
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
                  font=("Segoe UI", 12, "underline"),
                  bg="#0984e3", fg="white",
                  command=self.ir_registro).pack(pady=6)

    def login(self):
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
            cursor.execute(
                "SELECT id, rol FROM usuarios WHERE usuario = ? AND password = ?",
                (usuario, password)
            )
            row = cursor.fetchone()
            if row:
                user_id, rol = row
                print(f"[DEBUG] Valor de rol leído directamente de la base de datos: '{rol}'")
                self.controlador.usuario = usuario
                self.controlador.usuario_rol = rol.strip().lower() # Normalizamos el rol
                print(f"[DEBUG] Rol normalizado para la aplicación: '{self.controlador.usuario_rol}'")
                messagebox.showinfo("Login exitoso", f"¡Bienvenido {usuario}!")
                self.controlador.cargar_container()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos:\n{e}")
        finally:
            conn.close()

    def ir_registro(self):
        self.controlador.show_frame("Registro")

# ---------- Registro ----------
class Registro(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent, bg="#f5f6fa")
        self.controlador = controlador
        self.place(x=0, y=0, width=1100, height=650)
        self._build()

    def _build(self):
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
            cursor.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (?, ?, ?)", (usuario, password, 'usuario'))
            conn.commit()
            messagebox.showinfo("Registro exitoso", f"Usuario {usuario} registrado correctamente.")
            self.ir_login()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar usuario:\n{e}")
        finally:
            conn.close()

    def ir_login(self):
        self.controlador.show_frame("Login")


# ---------- Administración de Usuarios ----------
class AdminUsuarios(tk.Frame):
    def __init__(self, parent, controlador):
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
        tk.Label(self, text="Administrar Usuarios", font=("Segoe UI", 20, "bold"), bg="#f5f6fa").pack(pady=10)
        self.listbox = tk.Listbox(self, width=70, height=20)
        self.listbox.pack(pady=10)
        frame_btns = tk.Frame(self, bg="#f5f6fa")
        frame_btns.pack(pady=10)
        tk.Button(frame_btns, text="Crear Usuario", command=self.crear_usuario).grid(row=0, column=0, padx=5)
        tk.Button(frame_btns, text="Modificar Usuario", command=self.modificar_usuario).grid(row=0, column=1, padx=5)
        tk.Button(frame_btns, text="Asignar Rol", command=self.asignar_rol).grid(row=0, column=2, padx=5)
        tk.Button(frame_btns, text="Borrar Usuario", command=self.borrar_usuario).grid(row=0, column=3, padx=5)
        tk.Button(frame_btns, text="Actualizar Lista", command=self.cargar_usuarios).grid(row=0, column=4, padx=5)
        tk.Button(frame_btns, text="Cerrar Sesión", command=self.cerrar_sesion).grid(row=0, column=5, padx=5)
        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.listbox.delete(0, tk.END)
        try:
            usuarios = self.dao.consultar_usuarios()
            for u in usuarios:
                self.listbox.insert(tk.END, f"{u[0]} - {u[1]} - {u[2]}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar usuarios:\n{e}")

    def obtener_usuario_seleccionado(self):
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un usuario primero")
            return None
        texto = self.listbox.get(seleccion[0])
        return int(texto.split(" - ")[0])

    def crear_usuario(self):
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