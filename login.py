import pyodbc
import tkinter as tk
from tkinter import messagebox
from container import Container

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

# ---------- Widget Entrada Redondeada ----------
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

        # Entry
        self.entry = tk.Entry(self, bd=0, bg="#ecf0f1", font=("Segoe UI", 11))
        # Colocamos el Entry encima visualmente
        self.entry.place(x=12, y=10, width=self.width_px - 24, height=self.height_px - 20)

        # Placeholder visible (sin *)
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
        if self._has_placeholder:
            return ""
        return self.entry.get()

    def clear(self):
        self.entry.delete(0, tk.END)
        self._on_focus_out(None)

# ---------- LOGIN ----------
class Login(tk.Frame):
    def __init__(self, parent, controlador):
        super().__init__(parent, bg="#f5f6fa")
        self.controlador = controlador
        self.place(x=0, y=0, width=1100, height=650)
        self._build()

    def _build(self):
        # Tarjeta central más grande
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
                  activebackground="#74b9ff", activeforeground="white",
                  cursor="hand2", relief="flat",
                  width=22, height=2,
                  command=self.login).pack(pady=(26, 8))

        # Separador + link registro (siempre visible)
        sep = tk.Frame(card, bg="#eef2f5", height=2)
        sep.pack(fill="x", padx=40, pady=8)

        tk.Button(card, text="¿No tienes cuenta? Crear cuenta",
                  font=("Segoe UI", 10, "underline"),
                  bg="#ffffff", fg="#0984e3",
                  cursor="hand2", relief="flat",
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
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND password = ?", (usuario, password))
            ok = cursor.fetchone()[0] == 1
            if ok:
                messagebox.showinfo("Login exitoso", f"¡Bienvenido {usuario}!")
                self.controlador.show_frame(Container)
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar la base de datos:\n{e}")
        finally:
            conn.close()

    def ir_registro(self):
        self.controlador.show_frame(Registro)

# ---------- REGISTRO ----------
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
                  activebackground="#2ecc71", activeforeground="white",
                  cursor="hand2", relief="flat",
                  width=22, height=2,
                  command=self.registrar).pack(pady=(26, 8))

        sep = tk.Frame(card, bg="#eef2f5", height=2)
        sep.pack(fill="x", padx=40, pady=8)

        tk.Button(card, text="Volver al Login",
                  font=("Segoe UI", 10, "underline"),
                  bg="#ffffff", fg="#0984e3",
                  cursor="hand2", relief="flat",
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
