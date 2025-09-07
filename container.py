from tkinter import *
import tkinter as tk
from login import Ventas, Inventario, Clientes, AdminUsuarios 
import sys
import os

class Container(Frame):
    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.controlador = controlador
        self.place(x=0, y=0, width=1100, height=650)
        self.frames = {}
        self.cargar_frames_por_rol()
        self.widgets()
        self.show_frames("Ventas")

    def cargar_frames_por_rol(self):
        ventas_frame = Ventas(self, self.controlador)
        ventas_frame.place(x=0, y=40, width=1100, height=610)
        self.frames["Ventas"] = ventas_frame

        # Clientes: admin, empleado y usuario
        if self.controlador.usuario_rol in ("admin", "empleado", "usuario"):
            clientes_frame = Clientes(self, self.controlador)
            clientes_frame.place(x=0, y=40, width=1100, height=610)
            self.frames["Clientes"] = clientes_frame
            
            inventario_frame = Inventario(self, self.controlador)
            inventario_frame.place(x=0, y=40, width=1100, height=610)
            self.frames["Inventario"] = inventario_frame

        # Solo admin tiene Administrar Usuarios
        if self.controlador.usuario_rol == "admin":
            admin_frame = AdminUsuarios(self, self.controlador)
            admin_frame.place(x=0, y=40, width=1100, height=610)
            self.frames["AdminUsuarios"] = admin_frame

    def show_frames(self, nombre_frame):
        if nombre_frame in self.frames:
            frame = self.frames[nombre_frame]
            frame.tkraise()
        else:
            print(f"[WARN] El frame '{nombre_frame}' no existe para este rol.")

    def widgets(self):
        barra = tk.Frame(self, bg="#f1f2f6")
        barra.place(x=0, y=0, width=1100, height=40)
        
        for i in range(5):
            barra.grid_columnconfigure(i, weight=1)
        
        # Botón Ventas (siempre visible)
        self.btn_ventas = Button(barra, fg="black", text="Ventas", font="sans 14 bold",
                                 command=lambda: self.show_frames("Ventas"))
        self.btn_ventas.grid(row=0, column=0, sticky="nsew")

        # Botón Administrar Usuarios (solo para 'admin')
        if self.controlador.usuario_rol == "admin":
            self.btn_admin = Button(barra, fg="black", text="Administrar Usuarios", font="sans 14 bold",
                                     command=lambda: self.show_frames("AdminUsuarios"))
            self.btn_admin.grid(row=0, column=2, sticky="nsew")

        # Botón Clientes e Inventario(para 'admin', 'empleado' y 'usuario')
        if self.controlador.usuario_rol in ("admin", "empleado", "usuario"):
            self.btn_inventario = Button(barra, fg="black", text="Inventario", font="sans 14 bold",
                                         command=lambda: self.show_frames("Inventario"))
            self.btn_inventario.grid(row=0, column=1, sticky="nsew")
            self.btn_clientes = Button(barra, fg="black", text="Clientes", font="sans 14 bold",
                                         command=lambda: self.show_frames("Clientes"))
            self.btn_clientes.grid(row=0, column=3, sticky="nsew")

        # Botón Cerrar sesión 
        self.btn_logout = Button(barra, fg="red", text="Cerrar Sesión", font="sans 14 bold",
                                 command=lambda: self.controlador.logout())
        self.btn_logout.grid(row=0, column=4, sticky="nsew")