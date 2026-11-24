"""
ROPA YOJAN
Sistema de productos inventario y ventas con interfaz gráfica Tkinter

Archivos de dats:
- productos.txt: codigo,nombre,precio,cantidad
- ventas.txt: codigo,nombre,precio,cantidad vendida,total,fecha hora.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

ARCHIVO_PRODUCTOS = "productos.txt"
ARCHIVO_VENTAS = "ventas.txt"


def crear_archivos():
    """Crea los archivos de datos si todavía no existen."""
    for nombre in (ARCHIVO_PRODUCTOS, ARCHIVO_VENTAS):
        if not os.path.exists(nombre):
            with open(nombre, "w", encoding="utf-8") as archivo:
                pass


def cargar_productos():
    """Lee los productos y devuelve una lista de diccionarios."""
    productos = []
    errores = 0

    with open(ARCHIVO_PRODUCTOS, "r", encoding="utf-8") as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            datos = linea.rstrip("\n").split("|")
            if len(datos) != 4:
                errores += 1
                continue
            try:
                codigo, nombre = datos[0], datos[1]
                precio, cantidad = int(datos[2]), int(datos[3])
                if not codigo or not nombre or precio <= 0 or cantidad < 0:
                    raise ValueError
                productos.append({
                    "codigo": codigo,
                    "nombre": nombre,
                    "precio": precio,
                    "cantidad": cantidad
                })
            except ValueError:
                errores += 1

    if errores:
        messagebox.showwarning(
            "Datos con problemas",
            f"Se encontraron {errores} registro(s) inválido(s) en {ARCHIVO_PRODUCTOS}. "
            "Esos registros no se cargaron."
        )
    return productos


def guardar_productos(productos):
    """Guarda todos los productos usando un archivo temporal para evitar escrituras incompletas."""
    temporal = ARCHIVO_PRODUCTOS + ".tmp"
    with open(temporal, "w", encoding="utf-8") as archivo:
        for p in productos:
            archivo.write(
                f'{p["codigo"]}|{p["nombre"]}|{p["precio"]}|{p["cantidad"]}\n'
            )
    os.replace(temporal, ARCHIVO_PRODUCTOS)


def registrar_venta_en_archivo(producto, cantidad, total):
    """Agrega una venta al historial con fecha y hora."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARCHIVO_VENTAS, "a", encoding="utf-8") as archivo:
        archivo.write(
            f'{producto["codigo"]}|{producto["nombre"]}|{producto["precio"]}|'
            f'{cantidad}|{total}|{fecha}\n'
        )


def formato_dinero(valor):
    """Muestra valores en pesos con separador de miles."""
    return "$ " + format(valor, ",").replace(",", ".")


class AplicacionRopaYojan:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("ROPA YOJAN | Inventario y ventas")
        self.ventana.geometry("980x650")
        self.ventana.minsize(820, 560)
        self.ventana.configure(bg="#f3f5f8")

        crear_archivos()
        self.productos = []
        self.crear_estilos()
        self.crear_interfaz()
        self.actualizar_inventario()

    def crear_estilos(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("Arial", 22, "bold"),
                         background="#172554", foreground="white")
        estilo.configure("Subtitulo.TLabel", font=("Arial", 10),
                         background="#172554", foreground="#dbeafe")
        estilo.configure("Treeview", rowheight=28, font=("Arial", 10))
        estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        estilo.configure("Accion.TButton", font=("Arial", 10, "bold"), padding=8)

    def crear_interfaz(self):
        encabezado = tk.Frame(self.ventana, bg="#172554", padx=22, pady=16)
        encabezado.pack(fill="x")
        ttk.Label(encabezado, text="ROPA YOJAN", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            encabezado,
            text="Sistema de registro de productos, control de inventario y ventas",
            style="Subtitulo.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        contenedor = tk.Frame(self.ventana, bg="#f3f5f8", padx=18, pady=14)
        contenedor.pack(fill="both", expand=True)

        formulario = ttk.LabelFrame(contenedor, text="Datos del producto", padding=12)
        formulario.pack(fill="x", pady=(0, 12))

        self.codigo_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.precio_var = tk.StringVar()
        self.cantidad_var = tk.StringVar()

        campos = [
            ("Código", self.codigo_var),
            ("Nombre de la prenda", self.nombre_var),
            ("Precio (pesos)", self.precio_var),
            ("Cantidad inicial", self.cantidad_var),
        ]
        for columna, (texto, variable) in enumerate(campos):
            ttk.Label(formulario, text=texto).grid(row=0, column=columna, sticky="w", padx=6, pady=(0, 5))
            ttk.Entry(formulario, textvariable=variable, width=23).grid(
                row=1, column=columna, sticky="ew", padx=6
            )
            formulario.columnconfigure(columna, weight=1)

        botones = ttk.Frame(formulario)
        botones.grid(row=2, column=0, columnspan=4, sticky="w", padx=4, pady=(12, 0))
        ttk.Button(botones, text="Registrar producto", style="Accion.TButton",
                   command=self.registrar_producto).pack(side="left", padx=3)
        ttk.Button(botones, text="Limpiar campos",
                   command=self.limpiar_campos).pack(side="left", padx=3)

        zona_tabla = ttk.LabelFrame(contenedor, text="Inventario", padding=10)
        zona_tabla.pack(fill="both", expand=True)

        columnas = ("codigo", "nombre", "precio", "cantidad")
        self.tabla = ttk.Treeview(zona_tabla, columns=columnas, show="headings", height=10)
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Prenda")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("cantidad", text="Existencias")
        self.tabla.column("codigo", width=110, anchor="center")
        self.tabla.column("nombre", width=350)
        self.tabla.column("precio", width=160, anchor="e")
        self.tabla.column("cantidad", width=120, anchor="center")
        barra = ttk.Scrollbar(zona_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        acciones = ttk.Frame(contenedor)
        acciones.pack(fill="x", pady=12)
        ttk.Button(acciones, text="Actualizar inventario",
                   command=self.actualizar_inventario).pack(side="left", padx=3)
        ttk.Button(acciones, text="Registrar venta",
                   style="Accion.TButton", command=self.registrar_venta).pack(side="left", padx=3)
        ttk.Button(acciones, text="Consultar historial de ventas",
                   command=self.consultar_ventas).pack(side="left", padx=3)
        ttk.Button(acciones, text="Salir", command=self.salir).pack(side="right", padx=3)

        self.estado_var = tk.StringVar(value="Sistema listo.")
        tk.Label(self.ventana, textvariable=self.estado_var, anchor="w",
                 bg="#e2e8f0", fg="#334155", padx=14, pady=7).pack(fill="x")

    def limpiar_campos(self):
        self.codigo_var.set("")
        self.nombre_var.set("")
        self.precio_var.set("")
        self.cantidad_var.set("")

    def validar_producto(self):
        codigo = self.codigo_var.get().strip()
        nombre = self.nombre_var.get().strip()
        precio_texto = self.precio_var.get().strip()
        cantidad_texto = self.cantidad_var.get().strip()

        if not all((codigo, nombre, precio_texto, cantidad_texto)):
            messagebox.showerror("Datos incompletos", "Todos los campos son obligatorios.")
            return None

        if "|" in codigo or "|" in nombre or "\n" in codigo or "\n" in nombre:
            messagebox.showerror("Dato inválido", "No use el símbolo | ni saltos de línea en código o nombre.")
            return None

        try:
            precio = int(precio_texto)
            cantidad = int(cantidad_texto)
        except ValueError:
            messagebox.showerror("Dato inválido", "El precio y la cantidad deben ser números enteros.")
            return None

        if precio <= 0:
            messagebox.showerror("Precio inválido", "El precio debe ser mayor que cero.")
            return None
        if cantidad < 0:
            messagebox.showerror("Cantidad inválida", "La cantidad no puede ser negativa.")
            return None

        return {"codigo": codigo, "nombre": nombre, "precio": precio, "cantidad": cantidad}

    def registrar_producto(self):
        producto = self.validar_producto()
        if producto is None:
            return

        if any(p["codigo"].casefold() == producto["codigo"].casefold() for p in self.productos):
            messagebox.showerror("Código repetido", "Ya existe un producto con ese código.")
            return

        self.productos.append(producto)
        try:
            guardar_productos(self.productos)
        except OSError as error:
            self.productos.pop()
            messagebox.showerror("Error al guardar", f"No se pudo guardar el producto.\n{error}")
            return

        self.actualizar_inventario()
        self.limpiar_campos()
        self.estado_var.set(f'Producto "{producto["nombre"]}" registrado correctamente.')
        messagebox.showinfo("Registro exitoso", "El producto se registró correctamente.")

    def actualizar_inventario(self):
        try:
            self.productos = cargar_productos()
        except OSError as error:
            messagebox.showerror("Error de lectura", f"No se pudo leer el inventario.\n{error}")
            return

        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        for p in self.productos:
            self.tabla.insert("", "end", values=(
                p["codigo"], p["nombre"], formato_dinero(p["precio"]), p["cantidad"]
            ))
        self.estado_var.set(f"Productos registrados: {len(self.productos)}")

    def registrar_venta(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Seleccione un producto", "Seleccione una prenda de la tabla para vender.")
            return

        valores = self.tabla.item(seleccion[0], "values")
        codigo = str(valores[0])
        producto = next((p for p in self.productos if p["codigo"] == codigo), None)
        if producto is None:
            messagebox.showerror("Producto no encontrado", "Actualice el inventario e intente de nuevo.")
            return

        if producto["cantidad"] == 0:
            messagebox.showwarning("Sin existencias", "Este producto no tiene unidades disponibles.")
            return

        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("Registrar venta")
        dialogo.resizable(False, False)
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        marco = ttk.Frame(dialogo, padding=18)
        marco.pack(fill="both", expand=True)

        ttk.Label(marco, text=f'Producto: {producto["nombre"]}').pack(anchor="w", pady=4)
        ttk.Label(marco, text=f'Precio unitario: {formato_dinero(producto["precio"])}').pack(anchor="w", pady=4)
        ttk.Label(marco, text=f'Unidades disponibles: {producto["cantidad"]}').pack(anchor="w", pady=4)
        ttk.Label(marco, text="Cantidad que desea vender:").pack(anchor="w", pady=(12, 4))
        cantidad_var = tk.StringVar()
        entrada = ttk.Entry(marco, textvariable=cantidad_var, width=20)
        entrada.pack(anchor="w")
        entrada.focus_set()

        def confirmar():
            texto = cantidad_var.get().strip()
            if not texto.isdigit():
                messagebox.showerror("Cantidad inválida", "Ingrese una cantidad entera mayor que cero.", parent=dialogo)
                return
            cantidad = int(texto)
            if cantidad <= 0:
                messagebox.showerror("Cantidad inválida", "La cantidad debe ser mayor que cero.", parent=dialogo)
                return
            if cantidad > producto["cantidad"]:
                messagebox.showerror("Existencias insuficientes",
                                     "No hay suficientes unidades disponibles.", parent=dialogo)
                return

            total = producto["precio"] * cantidad
            cantidad_anterior = producto["cantidad"]
            producto["cantidad"] -= cantidad
            try:
                guardar_productos(self.productos)
                registrar_venta_en_archivo(producto, cantidad, total)
            except OSError as error:
                producto["cantidad"] = cantidad_anterior
                try:
                    guardar_productos(self.productos)
                except OSError:
                    pass
                messagebox.showerror("Error al guardar", f"No se pudo completar la venta.\n{error}", parent=dialogo)
                return

            dialogo.destroy()
            self.actualizar_inventario()
            self.estado_var.set(f"Venta registrada. Total: {formato_dinero(total)}")
            messagebox.showinfo(
                "Venta registrada",
                f'Prenda: {producto["nombre"]}\n'
                f'Cantidad vendida: {cantidad}\n'
                f'Total: {formato_dinero(total)}\n'
                f'Unidades restantes: {producto["cantidad"]}'
            )

        ttk.Button(marco, text="Confirmar venta", command=confirmar).pack(anchor="w", pady=14)
        entrada.bind("<Return>", lambda evento: confirmar())

    def consultar_ventas(self):
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Historial de ventas - Ropa Yojan")
        ventana.geometry("850x420")
        ventana.transient(self.ventana)

        marco = ttk.Frame(ventana, padding=12)
        marco.pack(fill="both", expand=True)
        columnas = ("codigo", "nombre", "precio", "cantidad", "total", "fecha")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = {
            "codigo": "Código", "nombre": "Prenda", "precio": "Precio unitario",
            "cantidad": "Cantidad", "total": "Total", "fecha": "Fecha y hora"
        }
        anchos = {"codigo": 80, "nombre": 160, "precio": 120, "cantidad": 80, "total": 120, "fecha": 160}
        for col in columnas:
            tabla.heading(col, text=encabezados[col])
            tabla.column(col, width=anchos[col], anchor="center")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        total_vendido = 0
        cantidad_registros = 0
        try:
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.rstrip("\n").split("|")
                    if len(datos) not in (5, 6):
                        continue
                    try:
                        codigo, nombre = datos[0], datos[1]
                        precio, cantidad, total = int(datos[2]), int(datos[3]), int(datos[4])
                    except ValueError:
                        continue
                    fecha = datos[5] if len(datos) == 6 else "Registro anterior"
                    tabla.insert("", "end", values=(
                        codigo, nombre, formato_dinero(precio), cantidad, formato_dinero(total), fecha
                    ))
                    total_vendido += total
                    cantidad_registros += 1
        except OSError as error:
            messagebox.showerror("Error de lectura", f"No se pudo leer el historial.\n{error}", parent=ventana)
            ventana.destroy()
            return

        ttk.Label(
            ventana,
            text=f"Ventas registradas: {cantidad_registros}     Total vendido: {formato_dinero(total_vendido)}",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=14, pady=10)

    def salir(self):
        if messagebox.askyesno("Salir", "¿Desea cerrar el sistema Ropa Yojan?"):
            self.ventana.destroy()


if __name__ == "__main__":
    ventana_principal = tk.Tk()
    aplicacion = AplicacionRopaYojan(ventana_principal)
    ventana_principal.mainloop()
