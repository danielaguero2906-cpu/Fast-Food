"""

================

Este módulo define la clase `Container`, que administra los diferentes
frames (Ventas, Inventario, Clientes, AdminUsuarios) según el rol del usuario.

Clases:
    Container: Frame principal que contiene y organiza los módulos de la aplicación.
"""

from tkinter import *
from login import  AdminUsuarios
from Ventas import Ventas
from inventario import Inventario
from clientes import Clientes
from tkinter import messagebox
import tkinter as tk


class Container(Frame):
    """
    Frame contenedor de los diferentes módulos de la aplicación.

    Dependiendo del rol del usuario, carga y muestra:
        - Ventas (todos los roles)
        - Clientes e Inventario (roles: admin, empleado, usuario)
        - AdminUsuarios (solo admin)
    """

    def __init__(self, padre, controlador):
        """
        Inicializa el contenedor.

        Args:
            padre (tk.Tk | tk.Frame): Ventana o frame padre.
            controlador (Manager): Instancia principal que maneja sesión y navegación.
        """
        super().__init__(padre)
        self.controlador = controlador
        self.frames = {}

        self.widgets()
        self.cargar_frames_por_rol()
        self.show_frame("Ventas")
        self.bind("<<ClienteAgregado>>", lambda e: self.cargar_clientes())

    def cargar_frames_por_rol(self):
        """
        Carga los frames disponibles según el rol del usuario.

        Roles y accesos:
            - Todos: Ventas
            - Admin, Empleado, Usuario: Clientes, Inventario
            - Admin: AdminUsuarios
        """
        rol = self.controlador.usuario_rol
        print(f"[DEBUG] Container se carga con rol: {rol}")

        # Limpiar frames antiguos
        for f in self.frames.values():
            f.destroy()
        self.frames.clear()

        # Todos los roles tienen Ventas y Clientes
        self.frames["Ventas"] = Ventas(self, self.controlador)
        self.frames["Ventas"].place(x=0, y=40, width=1100, height=610)

        if rol in ("admin", "empleado", "usuario"):
            self.frames["Clientes"] = Clientes(self, self.controlador)
            self.frames["Clientes"].place(x=0, y=40, width=1100, height=610)

        # Admin Usuarios e Inventario solo admin
        if rol == "admin":
            self.frames["AdminUsuarios"] = AdminUsuarios(self, self.controlador)
            self.frames["AdminUsuarios"].place(x=0, y=40, width=1100, height=610)
            
            self.frames["Inventario"] = Inventario(self, self.controlador)
            self.frames["Inventario"].place(x=0, y=40, width=1100, height=610)

    def show_frame(self, nombre):
        """
        Muestra el frame indicado por nombre.

        Args:
            nombre (str): Nombre del frame a mostrar.
        """
        if nombre in self.frames:
            self.frames[nombre].tkraise()
        else:
            print(f"[WARN] El frame '{nombre}' no existe para este rol.")
            messagebox.showerror("Acceso denegado", "Vista no permitida para este usuario")

    def widgets(self):
        """
        Crea la barra superior de navegación con botones dinámicos según el rol.

        Botones:
            - Ventas: todos los roles.
            - Clientes: admin, empleado, usuario.
            - Administrar Usuarios, Inventario: solo admin.
            - Cerrar sesión: todos los roles.
        """
        barra = tk.Frame(self, bg="#f1f2f6")
        barra.place(x=0, y=0, width=1100, height=40)

        rol = self.controlador.usuario_rol

        for i in range(5):
            barra.grid_columnconfigure(i, weight=1)

        # Botón Ventas
        Button(barra, text="Ventas", font="sans 14 bold",
               command=lambda: self.show_frame("Ventas")).grid(row=0, column=0, sticky="nsew")

        # Botón Inventario
        if rol in ("admin", "empleado", "usuario"):
            Button(barra, text="Inventario", font="sans 14 bold",
                   command=lambda: self.show_frame("Inventario")).grid(row=0, column=1, sticky="nsew")

        # Botón Clientes
        if rol in ("admin", "empleado", "usuario"):
            Button(barra, text="Clientes", font="sans 14 bold",
                   command=lambda: self.show_frame("Clientes")).grid(row=0, column=2, sticky="nsew")

        # Botón AdminUsuarios
        if rol in ("admin", "empleado"):
            Button(barra, text="Administrar Usuarios", font="sans 14 bold",
                   command=lambda: self.show_frame("AdminUsuarios")).grid(row=0, column=3, sticky="nsew")

        # Botón Cerrar sesión
        Button(barra, text="Cerrar Sesión", fg="red", font="sans 14 bold",
               command=self.controlador.logout).grid(row=0, column=4, sticky="nsew")

