from tkinter import *
import tkinter as tk

class Clientes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#FFFFFF")
        self.widgets()

    def widgets(self):
        label = tk.Label(self, text="Gestión de Clientes", bg="#FFFFFF", font="sans 16 bold")
        label.pack(pady=20)