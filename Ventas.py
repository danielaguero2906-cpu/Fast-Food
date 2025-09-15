from tkinter import *
import tkinter as tk

class Ventas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.config(bg="#FFFFFF")
        self.widgets()

    def widgets(self):
        label = tk.Label(self, text="Gestión de Ventas", bg="#FFFFFF", font="sans 16 bold")
        label.pack(pady=20)