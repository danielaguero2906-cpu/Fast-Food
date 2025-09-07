from tkinter import *
from tkinter import ttk
from login import Login, Registro
from container import Container

class Manager(Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

        self.style = ttk.Style()
        self.style.theme_use("clam")

    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
        else:
            print(f"[WARN] No se encontró el frame: {name}")

    def cargar_container(self):
        if not self.usuario_rol:
            print("[ERROR] No se ha definido el rol del usuario.")
            return  
        
        self.usuario_rol = self.usuario_rol.strip().lower()
        print(f"[DEBUG] Rol normalizado: {self.usuario_rol}")

        # Si ya existe un Container, destruirlo para evitar duplicados
        if "Container" in self.frames:
            self.frames["Container"].destroy()
            del self.frames["Container"]

        # Crear el nuevo container según el rol actual
        container = Container(self, self)
        self.frames["Container"] = container
        container.place(x=0, y=0, width=1100, height=650)
        self.show_frame("Container")
        
    def logout(self):
        """Maneja la lógica para cerrar la sesión y volver a la pantalla de login."""
        # Destruir el contenedor actual y sus sub-frames
        if "Container" in self.frames:
            self.frames["Container"].destroy()
            del self.frames["Container"]
        
        # Restablecer las variables de sesión
        self.usuario = None
        self.usuario_rol = None

        # Mostrar la pantalla de Login
        self.show_frame("Login")


    def main():
        app = Manager()
        app.mainloop()

    if __name__ == "__main__":
        main()
