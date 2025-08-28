from tkinter import * 
import tkinter as tk  
from ventas import Ventas
from inventario import Inventario 
from clientes import Clientes     
from proveedor import Proveedores   
import sys
import os 

class Container(Frame):                                              
    def __init__(self, padre, controlador):                                          # Constructor de la clase, recibe el contenedor padre y el controlador
        super().__init__(padre)                          # Llama al constructor de la clase Frame con el padre
        self.controlador = controlador                              # Guarda el controlador como atributo de instancia
        self.place(x=0, y=0, width=1100, height=650)                        # Posiciona el frame en la ventana principal
        self.widgets()    
        self.frames = {}  
        self.buttons = []                                       # Lista para almacenar referencias a los botones

        for i in (Ventas, Inventario, Clientes, Pedidos, Proveedores):
            frame = i(self)  
            self.frames[i] = frame  # Almacena el frame en el diccionario con la clase como clave
            frame.pack()  # (NO recomendable junto con place) Empaqueta el frame (se puede eliminar)
            frame.config(bg="#C6D9E3", highlightbackground="gray", highlightthickness=1)  # Configura fondo y borde
            frame.place(x=0, y=40, width=1100, height=610)  # Posiciona el frame justo debajo de los botones        
        self.show_frames(Ventas) # Muestra el frame de Ventas por defecto al iniciar

    def show_frames(self, container):  # Método para mostrar un frame específico
        frame = self.frames[container]  # Obtiene el frame desde el diccionario
        frame.tkraise()  # Trae el frame al frente (hace visible el seleccionado)

    def ventas(self):
        self.show_frames(Ventas)  # Muestra el frame de Ventas

    def inventario(self):
        self.show_frames(Inventario)  # Muestra el frame de Inventario

    def clientes(self):
        self.show_frames(Clientes)  # Muestra el frame de Clientes

    def pedidos(self):
        self.show_frames(Pedidos)  # Muestra el frame de Pedidos

    def proveedor(self):
        self.show_frames(Proveedores)  # Muestra el frame de Proveedor  # Muestra el frame de Información

    def widgets(self):  # Método para crear los botones superiores de navegación
        frame2 = tk.Frame(self)  # Crea un frame para contener los botones
        frame2.place(x=0, y=0, width=1100, height=40)  # Posiciona el frame en la parte superior del contenedor

        # Crea cada botón con texto, estilo y función asociada, y lo posiciona horizontalmente
        self.btn_ventas = Button(frame2, fg="black", text="Ventas", font="sans 16 bold", command=self.ventas)
        self.btn_ventas.place(x=0, y=0, width=184, height=40)

        self.btn_inventario = Button(frame2, fg="black", text="Inventario", font="sans 16 bold", command=self.inventario)
        self.btn_inventario.place(x=184, y=0, width=184, height=40)

        self.btn_clientes = Button(frame2, fg="black", text="Clientes", font="sans 16 bold", command=self.clientes)
        self.btn_clientes.place(x=369, y=0, width=184, height=40)

        self.btn_pedidos = Button(frame2, fg="black", text="Pedidos", font="sans 16 bold", command=self.pedidos)
        self.btn_pedidos.place(x=554, y=0, width=184, height=40)

        self.btn_proveedor = Button(frame2, fg="black", text="Proveedor", font="sans 16 bold", command=self.proveedor)
        self.btn_proveedor.place(x=739, y=0, width=184, height=40)

        self.buttons = [self.btn_ventas, self.btn_inventario, self.btn_clientes, self.btn_pedidos, self.btn_proveedor]