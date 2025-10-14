import pyodbc
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import threading
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import os
import sys

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

class MetodoPagoFrame(tk.Toplevel):
    def __init__(self, parent, total_venta):
        super().__init__(parent)
        self.title("Seleccionar método de pago")
        self.geometry("400x300")
        self.config(bg="#2196F3")
        self.parent = parent
        self.total_venta = total_venta
        self.metodo = tk.StringVar(value="Efectivo")

        tk.Label(self, text="Método de pago", font=("Arial", 14, "bold"), bg="#2196F3", fg="white").pack(pady=10)

        for metodo in ["Efectivo", "Tarjeta de Débito", "Tarjeta de Crédito"]:
            tk.Radiobutton(self, text=metodo, variable=self.metodo, value=metodo, bg="#2196F3", fg="white", font=("Arial", 12)).pack(anchor="w", padx=30, pady=5)

        self.label_total = tk.Label(self, text=f"Total: {self.total_venta:.2f} Gs", bg="#2196F3", fg="white", font=("Arial", 14, "bold"))
        self.label_total.pack(pady=20)

        tk.Button(self, text="Confirmar", command=self.confirmar, font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.destroy, font=("Arial", 12, "bold")).pack()

    def confirmar(self):
        metodo = self.metodo.get()
        total_final = self.total_venta

        if metodo == "Tarjeta de Crédito":
            total_final *= 1.06  # +6% comisión

        self.destroy()
        VentanaPago(self.parent, metodo, total_final)
        
class VentanaPago(tk.Toplevel):
    def __init__(self, parent, metodo, total_final):
        super().__init__(parent)
        self.title("Pago del Cliente")
        self.geometry("400x300")
        self.config(bg="#2196F3")
        self.parent = parent
        self.metodo = metodo
        self.total_final = total_final

        tk.Label(self, text=f"Método: {metodo}", bg="#2196F3", fg="white", font=("Arial", 13, "bold")).pack(pady=10)
        tk.Label(self, text=f"Total a pagar: {total_final:.2f} Gs", bg="#2196F3", fg="white", font=("Arial", 13)).pack(pady=5)

        tk.Label(self, text="Monto abonado:", bg="#2196F3", fg="white", font=("Arial", 12)).pack(pady=10)
        self.entry_monto = tk.Entry(self, font=("Arial", 12))
        self.entry_monto.pack(pady=5)

        tk.Button(self, text="Confirmar pago", command=self.confirmar_pago, font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.destroy, font=("Arial", 12, "bold")).pack()

    def confirmar_pago(self):
        try:
            monto_abonado = float(self.entry_monto.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido.")
            return

        if monto_abonado < self.total_final:
            messagebox.showerror("Error", "El monto abonado es insuficiente.")
            return

        cambio = monto_abonado - self.total_final
        messagebox.showinfo("Pago exitoso", f"Pago con {self.metodo} realizado.\nCambio: {cambio:.2f} Gs")

        self.destroy()
        self.parent.registrar_pago(self.metodo, self.total_final)

class Ventas(tk.Frame):
    def __init__(self,padre, controlador):
        super().__init__(padre)
        self.numero_factura = self.obtener_numero_factura_actual()
        self.productos_seleccionados = []
        self.widgets()
        self.controlador = controlador
        self.padre = padre
        self.cargar_productos()
        self.cargar_clientes()
        self.timer_producto = None
        self.timer_cliente = None
        self.master.bind("<<ActualizarInventario>>", lambda e: self.cargar_productos())
        
    def obtener_numero_factura_actual(self):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT MAX(factura) FROM ventas")
            last_invoice_number = c.fetchone()[0]
            conn.close()
            return last_invoice_number + 1 if last_invoice_number is not None else 1
        except Exception as e:
            print("Error obteniendo el numero de factura actual: ", e)
            return 1
    
    def cargar_clientes(self):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute("SELECT nombre FROM clientes")
            clientes = c.fetchall()           
            self.clientes = [cliente[0] for cliente in clientes]
            self.entry_cliente["values"] = self.clientes
            conn.close()
        except Exception as e:
            print("Error cargando clientes: ", e)
            
    def filtrar_clientes(self, event):
        if self.timer_cliente:
            self.timer_cliente.cancel()
        self.timer_cliente = threading.Timer(0.5, self._filter_clientes)
        self.timer_cliente.start()
        
    def _filter_clientes(self): 
        typed = self.entry_cliente.get()
        
        if typed == '':
            data = self.clientes
        else:
            data = [item for item in self.clientes if typed.lower() in item.lower()]
            
        if data:
            self.entry_cliente['values'] = data
            self.entry_cliente.event_generate('<Down>')
            self.after(100, self.actualizar_stock)
        else:
            self.entry_cliente['values'] = []
       
    def cargar_productos(self):
        try:
            conn = conectar_db()
            if not conn: return
            c = conn.cursor()
            c.execute("SELECT articulo FROM articulos")
            self.products = [product[0] for product in c.fetchall()]
            self.entry_producto["values"] = self.products
            conn.close()
        except Exception as e:
            print("Error cargando productos: ", e)
            
    def filtrar_productos(self, event):
        if self.timer_producto:
            self.timer_producto.cancel()
        self.timer_producto = threading.Timer(0.5, self._filter_products)
        self.timer_producto.start()
        
    def _filter_products(self): 
        typed = self.entry_producto.get()
        
        if typed == '':
            data = self.products
        else:
            data = [item for item in self.products if typed.lower() in item.lower()]
            
        if data:
            self.entry_producto['values'] = data
            self.entry_producto.event_generate('<Down>')
            self.after(100, self.actualizar_stock)
        else:
            self.entry_producto['values'] = ['No se encontraron resultados']
            self.entry_producto.event_generate('<Down>')
            self.entry_producto.delete(0, tk.END)
            
    def agregar_articulo(self):
        cliente = self.entry_cliente.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()
        
        if not cliente or not producto or not cantidad:
            messagebox.showwarning("Campos incompletos", "Complete todos los campos antes de agregar.")
            return
        cliente = self.entry_cliente.get().strip()
        if cliente not in self.clientes:
            respuesta = messagebox.askyesno("Cliente no encontrado", 
                                    f"El cliente '{cliente}' no está registrado.\n¿Desea crearlo?")
            if respuesta:
                self.alta_rapida_cliente(cliente)
                return 
            
        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showwarning("Cantidad inválida", "Por favor ingrese una cantidad válida.")
            return

        cantidad = int(cantidad)
        cliente = self.entry_cliente.get()
          
        try:
            conn = conectar_db()
            c = conn.cursor()
            if hasattr(self, "item_en_edicion") and self.item_en_edicion:
                if hasattr(self, "producto_original") and hasattr(self, "cantidad_original"):
                    c.execute("UPDATE articulos SET stock = stock + ? WHERE articulo = ?",
                            (self.cantidad_original, self.producto_original))
                    conn.commit()

            c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (producto,))
            resultado = c.fetchone()
            
            if resultado is None: 
                messagebox.showerror("Error", "Producto no encontrado.")
                return
            
            precio, costo, stock = resultado
            
            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")
                return
            
            c.execute("UPDATE articulos SET stock = stock - ? WHERE articulo = ?", (cantidad, producto))
            conn.commit()

            total = precio * cantidad
            total_cop = "{:,.0f}".format(total)
            if hasattr(self, "item_en_edicion") and self.item_en_edicion:
                self.tre.delete(self.item_en_edicion)
                self.item_en_edicion = None

            self.tre.insert("", "end", values=(self.numero_factura, cliente, producto," {:,.0f}".format(precio), cantidad, total_cop))
            self.productos_seleccionados.append((self.numero_factura, cliente, producto, precio, cantidad, total_cop, costo))
            conn.close()
            
            self.entry_producto.set('')
            self.entry_cantidad.delete(0, 'end')
            self.entry_producto.focus() 
            
            self.calcular_precio_total()

        except Exception as e:
            print("Error al agregar articulo", e)
        
    def calcular_precio_total(self):
        total_pagar = sum(float(str(self.tre.item(item)["values"][-1]).replace(" ", "").replace(",", "")) for item in self.tre.get_children())
        total_pagar_cop = "{:,.0f}".format(total_pagar)
        self.label_precio_total.config(text=f"Precio a Pagar: $ {total_pagar_cop}")
    
    def actualizar_stock(self, event=None):
        producto_seleccionado = self.entry_producto.get()
        print("Actualizando stock para:", producto_seleccionado)
        
        try:
            conn = conectar_db()
            if not conn: return
            c = conn.cursor()
            c.execute("SELECT stock FROM articulos WHERE articulo=?", (producto_seleccionado,))
            result = c.fetchone()
            conn.close()
            
            if result is not None:
                stock = result[0]
                self.label_stock.config(text=f"Stock: {stock}")
            else:
               self.label_stock.config(text="Stock: N/A") 
        except Exception as e:
            print("Error al obtener el stock del producto: ", e)
    
    def realizar_pago(self):
        if not self.tre.get_children():
            messagebox.showerror("Error", "No hay productos seleccionados para realizar el pago.")
            return

        total_venta = 0
        
        for item in self.tre.get_children():
            valores = self.tre.item(item, "values")
            total_venta += float(valores[5]) 
        MetodoPagoFrame(self, total_venta)
        
    def registrar_pago(self, metodo, total_final):
        try:
            messagebox.showinfo("Venta registrada", f"Pago con {metodo}\nTotal cobrado: {total_final:.2f} Gs")
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la venta:\n{e}")
            
    def procesar_pago(self, cantidad_pagada, ventana_pago, total_venta):
        cantidad_pagada = float(cantidad_pagada)
        cliente = self.entry_cliente.get()
        
        if cantidad_pagada < total_venta:
            messagebox.showerror("Error", "La cantidad pagada es insuficiente.")
            return
        
        cambio = cantidad_pagada - total_venta
        
        total_formateado =  "{:,.0f}".format(total_venta)
        
        mensaje = f"Total: {total_formateado} \nCantidad Pagada: {cantidad_pagada:,.0f} \nCambio: {cambio:,.0f}"
        messagebox.showinfo("Pago realizado ", mensaje)
        
        try:
            conn = conectar_db()
            c = conn.cursor()
            
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
            
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.execute("INSERT INTO ventas (factura, cliente, articulo, precio, cantidad, total, costo, fecha, hora) VALUES (?,?,?,?,?,?,?,?,?)", 
                    (factura, cliente, producto, precio, cantidad, total.replace(" ", "").replace(",", ""), costo * cantidad, fecha_actual, hora_actual))

                c.execute("UPDATE articulos SET stock = stock - ? WHERE articulo = ? ", (cantidad, producto))
                
            conn.commit()
            
            self.generar_factura_pdf(total_venta, cliente)

        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar la venta: {e}")
            
        self.numero_factura += 1
        self.label_numero_factura.config(text=str(self.numero_factura))
        
        self.productos_seleccionados = []
        self.limpiar_campos()
        
        ventana_pago.destroy()
        
    def limpiar_campos(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.label_precio_total.config(text="Precio a pagar: $ 0")
        
        self.entry_producto.set('')
        self.entry_cantidad.delete(0, 'end')
        
    def limpiar_lista(self):
        self.tre.delete(*self.tre.get_children())
        self.productos_seleccionados.clear()
        self.calcular_precio_total()
        
    def eliminar_articulo(self):
        item_seleccionado = self.tre.selection()
        if not item_seleccionado:
            messagebox.showerror("Error", "No hay ningun articulo seleccionado")
            return
        
        item_id = item_seleccionado[0]
        valores_item = self.tre.item(item_id)["values"]
        factura, cliente, articulo, precio, cantidad, total = valores_item
        
        self.tre.delete(item_id)
        
        self.productos_seleccionados = [producto for producto in self.productos_seleccionados if producto[2] != articulo]
        self.calcular_precio_total()
        
    def editar_articulo(self):
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showerror("Error", "Por favor seleccione un articulo para editar")
            return
        
        item_values = self.tre.item(selected_item[0], 'values')
        if not item_values:
            return
        
        current_producto = item_values[2]
        current_cantidad = item_values[4]
        
        new_cantidad = simpledialog.askinteger("Editar Articulo", "Ingrese la nueva cantidad:", initialvalue=current_cantidad)
        
        if new_cantidad is not None:
            try:
                conn = conectar_db()
                c = conn.cursor()
                c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (current_producto,))
                resultado = c.fetchone()
                
                if resultado is None:
                    messagebox.showerror("Error", "Producto no encontrado")
        
                precio, costo, stock = resultado
                
                if new_cantidad > stock:
                    messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles")
                    return
                
                total = precio * new_cantidad
                total_cop = "{:,.0f} ".format(total)
                
                self.tre.item(selected_item[0], values= (self.numero_factura, self.entry_cliente.get(), current_producto, "{:,.0f}".format(precio), new_cantidad, total_cop))
                
                for idx, producto in enumerate(self.productos_seleccionados):
                    if producto[2] == current_producto:
                        self.productos_seleccionados[idx] = (self.numero_factura, self.entry_cliente.get(), current_producto, precio, new_cantidad, total_cop, costo)
                        break
                    
                conn.close()
                    
                self.calcular_precio_total()
            except Exception as e:
                print("Error al editar el articulo: ",e)    
    
    def ver_ventas_realizadas(self):
        try:
            conn = conectar_db()
            c = conn.cursor()
            c.execute(" SELECT * FROM ventas")
            ventas = c.fetchall()
            conn.close()
            
            ventana_ventas = tk.Toplevel(self)
            ventana_ventas.title("Ventas Realizadas")
            ventana_ventas.geometry("1100x650+120+20")
            ventana_ventas.configure(bg="#2196F3")
            ventana_ventas.resizable(False, False)
            ventana_ventas.transient(self.master)
            ventana_ventas.grab_set()
            ventana_ventas.focus_set()
            ventana_ventas.lift()
            
            def filtrar_ventas():
                factura_a_buscar = entry_factura.get()
                cliente_a_buscar = entry_cliente.get()
                for item in tree.get_children():
                    tree.delete(item)
                    
                ventas_filtradas = [
                    venta for venta in ventas
                    if (str(venta[0])== factura_a_buscar or not factura_a_buscar) and
                    (venta[1].lower()== cliente_a_buscar.lower() or not cliente_a_buscar)
                ]
                
                for venta in ventas_filtradas:
                    venta = list(venta)   
                    venta[3]= "{:,.0f}".format(venta[3])
                    venta[5]= "{:,.0f}".format(venta[5])   
                    fecha = venta[7]
                    
                    if hasattr(fecha, "strftime"):
                        venta[7] = fecha.strftime("%d-%m-%Y")   
                    else:
                        venta[7] = datetime.datetime.strptime(str(fecha), "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y")
                    tree.insert("", "end", values=venta)
                    
            label_ventas_realizadas = tk.Label(ventana_ventas, text="Ventas Realizadas", font="sans 26 bold", bg="#2196F3")
            label_ventas_realizadas.place(x=35, y=20)  
            
            filtro_frame = tk.Frame(ventana_ventas, bg="#2196F3")
            filtro_frame.place(x=20, y=60, width=1060, height=60) 
            
            label_factura = tk.Label(filtro_frame, text= "Numero de factura", bg="#2196F3", font="sans 14 bold")
            label_factura.place(x=10, y=15)
            
            entry_factura = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_factura.place(x=200, y=10, width=200, height=40)
            
            label_cliente = tk.Label(filtro_frame, text= "Cliente", bg="#2196F3", font="sans 14 bold")
            label_cliente.place(x=420, y=15)
            
            entry_cliente = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_cliente.place(x=620, y=10, width=200, height=40)
            
            btn_filtrar = tk.Button(filtro_frame, text="Filtrar", font="sans 14 bold", command=filtrar_ventas)
            btn_filtrar.place(x=840, y=10)
            
            tree_frame = tk.Frame(ventana_ventas, bg="white")
            tree_frame.place(x=20, y=130, width=1060, height=500)
            
            scrol_y = ttk.Scrollbar(tree_frame)
            scrol_y.pack(side=RIGHT, fill=Y)
            
            scrol_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
            scrol_x.pack(side=BOTTOM, fill=X)
            
            tree = ttk.Treeview(tree_frame, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora"), show="headings")
            tree.pack(expand=True, fill=BOTH)
            
            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)
            
            tree.heading("Factura", text="Factura")
            tree.heading("Cliente", text="Cliente")
            tree.heading("Producto", text="Producto")
            tree.heading("Precio", text="Precio")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha")
            tree.heading("Hora", text="Hora")
            
            tree.column("Factura", width=60, anchor="center")
            tree.column("Cliente", width=120, anchor="center")
            tree.column("Producto", width=120, anchor="center")
            tree.column("Precio", width=80, anchor="center")
            tree.column("Cantidad", width=80, anchor="center")
            tree.column("Total", width=80, anchor="center")
            tree.column("Fecha", width=80, anchor="center")
            tree.column("Hora", width=80, anchor="center")
            
            for venta in ventas:
                venta = list(venta)
                venta[3] = "{:,.0f}".format(venta[3])
                venta[5] = "{:,.0f}".format(venta[5]) 
                fecha = venta[7]
                if hasattr(fecha, "strftime"):
                    venta[7] = fecha.strftime("%d-%m-%Y")
                else:
                    venta[7] = str(fecha)
                tree.insert("", "end", values = (venta[0], venta[1], venta[2], venta[3], venta[4], venta[5], venta[6], venta[8]))
        except Exception as e:
            messagebox.showerror("Error",f"Error al obtener las ventas: {e}")
            
    def generar_factura_pdf(self, total_venta, cliente):
        try:
            os.makedirs("facturas", exist_ok=True)
            factura_path = os.path.join("facturas", f"Factura_{self.numero_factura}.pdf")

            c = canvas.Canvas(factura_path, pagesize = letter)
            
            empresa_nombre = "FAST FOOD"
            empresa_direccion = "Avda Brasilia 1234, Asuncion, Paraguay"
            empresa_telefono = "+595984135326"
            empresa_email = "fastfood@ff-fastfood.com.py"
            empresa_website = "https://www.fastfood.com.py/"
            
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(300, 750, "FACTURA DE VENTA")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50,710, f"{empresa_nombre}")
            c.setFont("Helvetica", 12)
            c.drawString(50,690, f"Direccion: {empresa_direccion}")
            c.drawString(50,670, f"Telefono: {empresa_telefono}")
            c.drawString(50,650, f"Email: {empresa_email}")
            c.drawString(50,630, f"Website: {empresa_website}")
            
            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(50, 620, 550, 620)
            
            c.setFont("Helvetica", 12)
            c.drawString(50,600, f"Numero de Factura: {self.numero_factura}")
            c.drawString(50,580, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            c.line(50, 560, 550, 560)
            
            c.drawString(50,540, f"Cliente: {cliente}")
            c.drawString(50,520, "Descripcion de Productos: ")
            
            y_offset = 500
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y_offset, "Producto")
            c.drawString(270, y_offset, "Cantidad")
            c.drawString(370, y_offset, "Precio")
            c.drawString(470, y_offset, "Total")
            
            c.line(50, y_offset - 10, 550, y_offset - 10)
            y_offset -= 30
            c.setFont("Helvetica", 12)
            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.setFont("Helvetica-Bold", 12)
                c.drawString(70, y_offset, producto)
                c.drawString(270, y_offset, str(cantidad))
                c.drawString(370, y_offset, "${:,.2f}".format(precio))
                c.drawString(470, y_offset, total)    
                y_offset -= 20
                
            c.line(50, y_offset, 550, y_offset)
            y_offset -= 20
            
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.darkblue)
            c.drawString(50, y_offset, f"Total a Pagar: ${total_venta:,.2f}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            
            y_offset -= 20
            c.line(50, y_offset, 550, y_offset)
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(150, y_offset -60, "Gracias por tu compra.Vuelve pronto")
            
            y_offset -= 100
            c.setFont("Helvetica", 10)
            c.drawString(50, y_offset, "Terminos y Condiciones:")
            c.drawString(50, y_offset -20, "1. Los productos entregados no tienen devolucion.")
            c.drawString(50, y_offset -40, "2. Conserve esta factura como comprobante de tu compra.")
            c.save()
            
            messagebox.showinfo("Factura generada", f"Se ha generado la factura en: {factura_path} ") 
            
            os.startfile(os.path.abspath(factura_path))
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")
                           
    def widgets(self):
       labelframe = tk.LabelFrame(self, font="arial 12 bold", bg="#2196F3")
       labelframe.place(x=25, y=30, width=1045, height=180)
       
       # === CLIENTE ===
       label_cliente = tk.Label(labelframe, text="Cliente: ", font="sans 14 bold", bg="#2196F3")
       label_cliente.place(x=10, y=11)
       self.entry_cliente = ttk.Combobox(labelframe, font="sans 14 bold")
       self.entry_cliente.place(x=120, y=8, width=260, height=40)
       self.entry_cliente.bind('<KeyRelease>', self.filtrar_clientes)
       self.entry_cliente.bind('<Return>', lambda e: self.entry_producto.focus())
       
       # === PRODUCTO ===
       label_producto = tk.Label(labelframe, text="Producto: ", font="sans 14 bold", bg="#2196F3")
       label_producto.place(x=10, y=70)
       self.entry_producto = ttk.Combobox(labelframe, font="sans 14 bold")
       self.entry_producto.place(x=120, y=66, width=260, height=40)
       self.entry_producto.bind('<KeyRelease>', self.filtrar_productos)
       self.entry_producto.bind("<FocusOut>", self.actualizar_stock)
       self.entry_producto.bind("<Return>", lambda e: self.entry_cantidad.focus())
       
       # === CANTIDAD ===
       label_cantidad = tk.Label(labelframe, text="Cantidad: ", font="sans 14 bold", bg="#2196F3")
       label_cantidad.place(x=500, y=11)
       self.entry_cantidad = ttk.Entry(labelframe, font="sans 14 bold")
       self.entry_cantidad.place(x=610, y=8, width=100, height=40)
       self.entry_cantidad.bind("<Return>", lambda e: self.agregar_y_reiniciar())  
       
       # === STOCK ===
       self.label_stock = tk.Label(labelframe, text="Stock: ", font="sans 14 bold", bg="#2196F3")
       self.label_stock.place(x=500, y=70)

        # === FACTURA ===
       label_factura = tk.Label(labelframe, text="Numero de Factura: ", font="sans 14 bold", bg="#2196F3")
       label_factura.place(x=750, y=11)
       self.label_numero_factura = tk.Label(labelframe, text=f"{self.numero_factura} ", font="sans 14 bold", bg="#2196F3")
       self.label_numero_factura.place(x= 950, y= 11)
       
       # === BOTONES ===
       boton_agregar = tk.Button(labelframe, text="Agregar Articulo", font="sans 14 bold", command=self.agregar_y_reiniciar)
       boton_agregar.place(x=90, y=120, width=200, height=40)

       boton_eliminar = tk.Button(labelframe, text="Eliminar Articulo", font="sans 14 bold", command=self.eliminar_articulo)
       boton_eliminar.place(x=310, y=120, width=200, height=40)
       
       boton_editar = tk.Button(labelframe, text="Editar Articulo", font="sans 14 bold", command= self.editar_articulo)
       boton_editar.place(x=530, y=120, width=200, height=40)
       
       boton_limpiar = tk.Button(labelframe, text="Limpiar lista", font="sans 14 bold", command=self.limpiar_lista)
       boton_limpiar.place(x=750, y=120, width=200, height=40)
       
       treFrame = tk.Frame(self, bg="white")
       treFrame.place(x=70, y=220, width=980, height=300)
       
       scrol_y = ttk.Scrollbar(treFrame)
       scrol_y.pack(side=RIGHT, fill=Y)
       scrol_x = ttk.Scrollbar(treFrame, orient=HORIZONTAL)
       scrol_x.pack(side=BOTTOM, fill=X)
       
       self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, height=40, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"), show="headings")
       self.tre.pack(expand=True, fill= BOTH)
       self.tre.bind("<Double-1>", self.editar_fila) # Doble click para editar
       
       scrol_y.config(command=self.tre.yview)
       scrol_x.config(command=self.tre.xview)
       
       self.tre.heading("Factura", text="Factura")
       self.tre.heading("Cliente", text="Cliente")
       self.tre.heading("Producto", text="Producto")
       self.tre.heading("Precio", text="Precio")
       self.tre.heading("Cantidad", text="Cantidad")
       self.tre.heading("Total", text="Total")
       
       self.tre.column("Factura", width=70, anchor="center")
       self.tre.column("Cliente", width=250, anchor="center")
       self.tre.column("Producto", width=250, anchor="center")
       self.tre.column("Precio", width=120, anchor="center")
       self.tre.column("Cantidad", width=120, anchor="center")
       self.tre.column("Total", width=150, anchor="center")
       
       self.label_precio_total = tk.Label(self, text= "Precio a pagar: $ 0", font="sans 18 bold", bg="#2196F3")
       self.label_precio_total.place(x=680, y=550)
       
       boton_pagar = tk.Button(self, text="Pagar", font="sans 14 bold", command=self.realizar_pago)
       boton_pagar.place(x=70, y=550, width=180, height=40)
       
       boton_ver_ventas = tk.Button(self, text="Ver Ventas realizadas", font="sans 14 bold", command=self.ver_ventas_realizadas)
       boton_ver_ventas.place(x=290, y=550, width=280, height=40)
       
       
    def agregar_y_reiniciar(self):
        """
        Agrega el artículo y luego limpia el campo de cantidad
        y devuelve el foco al campo producto.
        """
        self.agregar_articulo()
        self.entry_producto.set('') 
        self.entry_cantidad.delete(0, tk.END)
        self.entry_producto.focus()
       
    def editar_fila(self, event):
        """
        Permite editar un artículo cargado al hacer doble clic en la tabla.
        Carga los datos seleccionados en los campos correspondientes.
        """
        item = self.tre.selection()
        if not item:
            return
        
        valores = self.tre.item(item, "values")
        if not valores:
            return

        factura, cliente, producto, precio, cantidad, total = valores

        self.entry_cliente.set(cliente)
        self.entry_producto.set(producto)
        self.entry_cantidad.delete(0, tk.END)
        self.entry_cantidad.insert(0, cantidad)
        
        self.item_en_edicion = item
        self.producto_original = producto
        self.cantidad_original = cantidad
        self.entry_producto.focus()

    def alta_rapida_cliente(self, nombre_inicial=""):
        popup = tk.Toplevel(self)
        popup.title("Alta rápida de cliente")
        popup.geometry("350x150")
        popup.transient(self)
        popup.grab_set()

        tk.Label(popup, text="Nombre:").grid(row=0, column=0, padx=10, pady=10)
        nombre_entry = tk.Entry(popup, font=("Arial", 12))
        nombre_entry.grid(row=0, column=1, padx=10, pady=10)
        nombre_entry.insert(0, nombre_inicial)

        tk.Label(popup, text="Telefono:").grid(row=1, column=0, padx=10, pady=10)
        telefono_entry = tk.Entry(popup, font=("Arial", 12))
        telefono_entry.grid(row=1, column=1, padx=10, pady=10)

        def guardar_cliente():
            nombre = nombre_entry.get().strip()
            celular = telefono_entry.get().strip()

            if not nombre:
                messagebox.showwarning("Error", "El nombre es obligatorio.")
                return

            try:
                conn = conectar_db()
                c = conn.cursor()
                correo = "sin_correo@fastfood.com"
                cedula = "0000000"
                direccion = "Sin direccion"
                c.execute("INSERT INTO clientes (nombre, celular, correo, cedula, direccion) VALUES (?, ?, ?, ?, ?)", (nombre, celular, correo, cedula, direccion))
                conn.commit()
                conn.close()

                messagebox.showinfo("Éxito", f"Cliente '{nombre}' creado.")
                popup.destroy()
                
                self.cargar_clientes()
                self.entry_cliente.set(nombre)
                
                container = self.controlador.frames.get("Container")
                if container and "Clientes" in container.frames:
                    frame_clientes = container.frames["Clientes"]
                    if hasattr(frame_clientes, "cargar_registros"):
                        frame_clientes.cargar_registros()            
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el cliente:\n{e}")

        tk.Button(popup, text="Guardar", command=guardar_cliente).grid(row=2, column=0, columnspan=2, pady=10)
        nombre_entry.focus()


   
       