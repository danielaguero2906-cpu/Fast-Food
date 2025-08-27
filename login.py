import pyodbc
from tkinter import *   
import tkinter as tk  
from tkinter import ttk
from tkinter import messagebox

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
        messagebox.showerror("Error", f"No se pudo conectar a la BD:\n{e}")
        return None