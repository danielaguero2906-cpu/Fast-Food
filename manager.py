"""
Módulo manager
==============

Este módulo define la clase `Manager`, que actúa como ventana principal
de la aplicación Fast Food SPA.  
Se encarga de gestionar los distintos frames (Login, Registro y Container),
así como las variables de sesión del usuario.

Clases:
    Manager: Ventana raíz de la aplicación que coordina el flujo.

Funciones:
    main(): Punto de entrada para ejecutar la aplicación.
"""

from tkinter import *
from tkinter import ttk
from login import Login, Registro, AdminUsuarios
from container import Container


class Manager(Tk):
    """
    Clase principal de la aplicación Fast Food SPA.

    Hereda de `tk.Tk` y administra:
      - La ventana principal (root).
      - Los frames (Login, Registro y Container).
      - Variables de sesión (usuario y rol).
    """

    def __init__(self):
        """Inicializa la ventana principal y carga los frames básicos."""
        super().__init__()
        self.title("Fast Food SPA")
        self.geometry("1100x650+120+20")
        self.resizable(False, False)

        # Variables de sesión
        self.usuario = None
        self.usuario_rol = None

        self.frames = {}

        # Cargar Login y Registro
        for F in (Login, Registro):
            frame = F(self, self)
            self.frames[F.__name__] = frame
            frame.place(x=0, y=0, width=1100, height=650)

        self.show_frame("Login")

        # Estilo para widgets ttk
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def show_frame(self, name):
        """
        Muestra en pantalla el frame correspondiente al nombre.

        Args:
            name (str): Nombre de la clase del frame a mostrar.
        """
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
        else:
            print(f"[WARN] No se encontró el frame: {name}")

    def cargar_container(self):
        """
        Crea y muestra el frame `Container`.

        Se ejecuta tras un login exitoso, cargando los módulos
        correspondientes al rol del usuario.
        """
        if not self.usuario_rol:
            print("[ERROR] No se ha definido el rol del usuario.")
            return

        # Destruir container anterior si existe
        if "Container" in self.frames:
            self.frames["Container"].destroy()
            del self.frames["Container"]

        # Crear el container con frames según rol
        container = Container(self, self)
        self.frames["Container"] = container
        container.place(x=0, y=0, width=1100, height=650)
        self.show_frame("Container")

    def logout(self):
        """
        Cierra la sesión actual y vuelve a la pantalla de Login.
        """
        if "Container" in self.frames:
            self.frames["Container"].destroy()
            del self.frames["Container"]

        self.usuario = None
        self.usuario_rol = None
        self.show_frame("Login")


def main():
    """
    Punto de entrada principal de la aplicación.

    Crea una instancia de `Manager` y ejecuta el bucle principal de Tkinter.
    """
    app = Manager()
    app.mainloop()


if __name__ == "__main__":
    main()
