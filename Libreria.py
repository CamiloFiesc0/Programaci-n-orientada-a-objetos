#!/usr/bin/env python3
"""
libreria_cun.py
Sistema de consola para gestionar productos de la Librería Universitaria CUN.

Guardar / ejecutar: python libreria_cun.py
Datos persistentes: productos.json (creado en el mismo directorio)
Reportes: reportes/*.csv
Respaldos: backups/*.json

Funciones implementadas:
- Registrar producto (validación de código único)
- Consultar producto (por código, nombre o categoría)
- Modificar producto
- Eliminar producto (confirmación)
- Listar productos
- Control de stock (ajustar cantidades)
- Gestionar categorías (asignar / crear)
- Generar reporte CSV
- Respaldar datos (backup con timestamp)
- Salida segura (guarda antes de salir)
"""
import json
import csv
import os
import shutil
from datetime import datetime

DATA_FILE = "productos.json"
BACKUP_DIR = "backups"
REPORT_DIR = "reportes"

# ---------------------------
# Utilidades de persistencia
# ---------------------------
def ensure_dirs():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

def load_data():
    if not os.path.isfile(DATA_FILE):
        return {"productos": [], "categorias": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # en caso de archivo corrupto, devolver estructura vacía
        return {"productos": [], "categorias": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup_data():
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"productos_backup_{timestamp}.json")
    shutil.copy2(DATA_FILE, dest)
    print(f"Respaldo creado: {dest}")

# ---------------------------
# Operaciones sobre productos
# ---------------------------
def find_product_by_code(data, code):
    for p in data["productos"]:
        if p["codigo"].lower() == code.lower():
            return p
    return None

def find_products_by_name(data, name):
    name_lower = name.lower()
    return [p for p in data["productos"] if name_lower in p["nombre"].lower()]

def find_products_by_category(data, category):
    cat_lower = category.lower()
    return [p for p in data["productos"] if p.get("categoria","").lower() == cat_lower]

def input_non_empty(prompt):
    while True:
        v = input(prompt).strip()
        if v:
            return v
        print("Valor inválido: no puede estar vacío.")

def input_positive_int(prompt):
    while True:
        v = input(prompt).strip()
        try:
            n = int(v)
            if n >= 0:
                return n
            print("Ingrese un número entero >= 0.")
        except ValueError:
            print("Entrada inválida: ingrese un número entero.")

def input_positive_float(prompt):
    while True:
        v = input(prompt).strip()
        try:
            f = float(v)
            if f >= 0:
                return f
            print("Ingrese un número >= 0.")
        except ValueError:
            print("Entrada inválida: ingrese un número válido (ej. 12.50).")

def register_product(data):
    print("\n--- Registrar Producto ---")
    codigo = input_non_empty("Código (único): ")
    if find_product_by_code(data, codigo):
        print(f"[ERROR] Ya existe un producto con código '{codigo}'.")
        return
    nombre = input_non_empty("Nombre: ")
    print("Categorías existentes:", ", ".join(data["categorias"]) if data["categorias"] else "(ninguna)")
    categoria = input("Categoría (o dejar vacío para 'Sin categoría'): ").strip() or "Sin categoría"
    if categoria not in data["categorias"]:
        data["categorias"].append(categoria)
    cantidad = input_positive_int("Cantidad disponible: ")
    precio = input_positive_float("Precio unitario: ")
    descripcion = input("Descripción (opcional): ").strip()
    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "cantidad": cantidad,
        "precio": precio,
        "descripcion": descripcion,
        "fecha_creacion": datetime.now().isoformat()
    }
    data["productos"].append(producto)
    save_data(data)
    print("Producto registrado correctamente.")

def consult_product(data):
    print("\n--- Consultar Producto ---")
    print("Buscar por: 1) Código  2) Nombre  3) Categoría")
    choice = input("Seleccione opción (1/2/3): ").strip()
    if choice == "1":
        code = input_non_empty("Código: ")
        p = find_product_by_code(data, code)
        if p:
            print_product(p)
        else:
            print("No se encontró ningún producto con ese código.")
    elif choice == "2":
        name = input_non_empty("Nombre o parte del nombre: ")
        results = find_products_by_name(data, name)
        if results:
            print_products_table(results)
        else:
            print("No se encontraron coincidencias.")
    elif choice == "3":
        category = input_non_empty("Categoría: ")
        results = find_products_by_category(data, category)
        if results:
            print_products_table(results)
        else:
            print("No se encontraron productos en esa categoría.")
    else:
        print("Opción no válida.")

def modify_product(data):
    print("\n--- Modificar Producto ---")
    code = input_non_empty("Ingrese el código del producto a modificar: ")
    p = find_product_by_code(data, code)
    if not p:
        print("No existe un producto con ese código.")
        return
    print("Producto actual:")
    print_product(p)
    print("Deje vacío para no modificar un campo.")
    nombre = input("Nuevo nombre: ").strip()
    categoria = input("Nueva categoría: ").strip()
    if categoria and categoria not in data["categorias"]:
        data["categorias"].append(categoria)
    cantidad = input("Nueva cantidad: ").strip()
    precio = input("Nuevo precio: ").strip()
    descripcion = input("Nueva descripción: ").strip()
    # Aplicar cambios si se ingresó algo
    if nombre: p["nombre"] = nombre
    if categoria: p["categoria"] = categoria
    if cantidad:
        try:
            n = int(cantidad)
            if n >= 0:
                p["cantidad"] = n
            else:
                print("Cantidad no válida, se mantiene la anterior.")
        except ValueError:
            print("Cantidad no válida, se mantiene la anterior.")
    if precio:
        try:
            f = float(precio)
            if f >= 0:
                p["precio"] = f
            else:
                print("Precio no válido, se mantiene el anterior.")
        except ValueError:
            print("Precio no válido, se mantiene el anterior.")
    if descripcion: p["descripcion"] = descripcion
    p["fecha_modificacion"] = datetime.now().isoformat()
    save_data(data)
    print("Producto actualizado correctamente.")

def delete_product(data):
    print("\n--- Eliminar Producto ---")
    code = input_non_empty("Código del producto a eliminar: ")
    p = find_product_by_code(data, code)
    if not p:
        print("No existe un producto con ese código.")
        return
    print("Producto encontrado:")
    print_product(p)
    confirm = input("¿Confirma eliminación? (S/N): ").strip().lower()
    if confirm == "s":
        data["productos"] = [x for x in data["productos"] if x["codigo"].lower() != code.lower()]
        save_data(data)
        print("Producto eliminado.")
    else:
        print("Operación cancelada.")

def list_products(data):
    print("\n--- Listado de Productos ---")
    if not data["productos"]:
        print("(No hay productos registrados.)")
        return
    print_products_table(data["productos"])

def print_product(p):
    lines = [
        f"Código     : {p['codigo']}",
        f"Nombre     : {p['nombre']}",
        f"Categoría  : {p.get('categoria','')}",
        f"Cantidad   : {p.get('cantidad',0)}",
        f"Precio     : {p.get('precio',0):.2f}",
        f"Descripción: {p.get('descripcion','')}",
        f"Creado     : {p.get('fecha_creacion','')}",
        f"Modificado : {p.get('fecha_modificacion','')}"
    ]
    print("\n".join(lines))

def print_products_table(listado):
    # Imprimir tabla simple
    headers = ["CÓDIGO", "NOMBRE", "CATEGORÍA", "CANTIDAD", "PRECIO"]
    print("{:<12} {:<30} {:<15} {:>8} {:>10}".format(*headers))
    print("-"*80)
    for p in listado:
        print("{:<12} {:<30} {:<15} {:>8} {:>10.2f}".format(
            p["codigo"],
            (p["nombre"][:29] + "..") if len(p["nombre"])>31 else p["nombre"],
            p.get("categoria",""),
            p.get("cantidad",0),
            p.get("precio",0.0)
        ))

# ---------------------------
# Funciones avanzadas
# ---------------------------
def generate_report_csv(data):
    ensure_dirs()
    if not data["productos"]:
        print("No hay productos para generar reporte.")
        return
    filename = os.path.join(REPORT_DIR, f"reporte_productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["codigo","nombre","categoria","cantidad","precio","descripcion","fecha_creacion","fecha_modificacion"])
        for p in data["productos"]:
            writer.writerow([
                p.get("codigo",""),
                p.get("nombre",""),
                p.get("categoria",""),
                p.get("cantidad",""),
                f"{p.get('precio',0):.2f}",
                p.get("descripcion",""),
                p.get("fecha_creacion",""),
                p.get("fecha_modificacion","")
            ])
    print(f"Reporte generado: {filename}")

def backup_manual(data):
    # si no existe archivo, crear uno inicial
    save_data(data)
    backup_data()

def control_stock(data):
    print("\n--- Control de stock ---")
    code = input_non_empty("Código del producto: ")
    p = find_product_by_code(data, code)
    if not p:
        print("Producto no encontrado.")
        return
    print(f"Stock actual de '{p['nombre']}' ({p['codigo']}): {p['cantidad']}")
    print("Opciones: 1) Ajustar cantidad exacta  2) Aumentar  3) Disminuir")
    opt = input("Seleccione opción (1/2/3): ").strip()
    if opt == "1":
        n = input_positive_int("Ingrese nueva cantidad: ")
        p["cantidad"] = n
    elif opt == "2":
        n = input_positive_int("Cantidad a aumentar: ")
        p["cantidad"] += n
    elif opt == "3":
        n = input_positive_int("Cantidad a disminuir: ")
        if n > p["cantidad"]:
            print("No puede disminuir más que la cantidad disponible.")
            return
        p["cantidad"] -= n
    else:
        print("Opción inválida.")
        return
    p["fecha_modificacion"] = datetime.now().isoformat()
    save_data(data)
    print("Stock actualizado.")

def manage_categories(data):
    print("\n--- Gestión de categorías ---")
    print("Categorías actuales:", ", ".join(data["categorias"]) if data["categorias"] else "(ninguna)")
    print("Opciones: 1) Crear categoría  2) Renombrar categoría  3) Eliminar categoría")
    opt = input("Seleccione opción (1/2/3): ").strip()
    if opt == "1":
        cat = input_non_empty("Nombre de la nueva categoría: ")
        if cat in data["categorias"]:
            print("La categoría ya existe.")
            return
        data["categorias"].append(cat)
        save_data(data)
        print("Categoría creada.")
    elif opt == "2":
        old = input_non_empty("Categoría a renombrar: ")
        if old not in data["categorias"]:
            print("No existe la categoría.")
            return
        new = input_non_empty("Nuevo nombre: ")
        if new in data["categorias"]:
            print("Ya existe una categoría con ese nombre.")
            return
        # renombrar en lista y en productos asociados
        data["categorias"] = [new if c==old else c for c in data["categorias"]]
        for p in data["productos"]:
            if p.get("categoria","") == old:
                p["categoria"] = new
                p["fecha_modificacion"] = datetime.now().isoformat()
        save_data(data)
        print("Categoría renombrada y productos actualizados.")
    elif opt == "3":
        cat = input_non_empty("Categoría a eliminar: ")
        if cat not in data["categorias"]:
            print("No existe la categoría.")
            return
        # reasignar productos a 'Sin categoría' o eliminar categoría
        for p in data["productos"]:
            if p.get("categoria","") == cat:
                p["categoria"] = "Sin categoría"
                p["fecha_modificacion"] = datetime.now().isoformat()
        data["categorias"] = [c for c in data["categorias"] if c != cat]
        save_data(data)
        print("Categoría eliminada y productos reasignados a 'Sin categoría'.")
    else:
        print("Opción inválida.")

# ---------------------------
# Interfaz principal (menu)
# ---------------------------
def show_menu():
    print("\n" + "="*50)
    print(" Librería Universitaria CUN — Sistema de Gestión de Productos")
    print("="*50)
    print("1) Registrar producto")
    print("2) Consultar producto")
    print("3) Modificar producto")
    print("4) Eliminar producto")
    print("5) Listar productos")
    print("6) Control de stock")
    print("7) Gestión de categorías")
    print("8) Generar reporte CSV")
    print("9) Respaldar datos (backup)")
    print("0) Salir")
    print("="*50)

def main():
    ensure_dirs()
    data = load_data()
    # inicializar categorias si no existe
    if "categorias" not in data:
        data["categorias"] = []
    while True:
        show_menu()
        opt = input("Seleccione una opción: ").strip()
        if opt == "1":
            register_product(data)
        elif opt == "2":
            consult_product(data)
        elif opt == "3":
            modify_product(data)
        elif opt == "4":
            delete_product(data)
        elif opt == "5":
            list_products(data)
        elif opt == "6":
            control_stock(data)
        elif opt == "7":
            manage_categories(data)
        elif opt == "8":
            generate_report_csv(data)
        elif opt == "9":
            save_data(data)
            backup_manual(data)
        elif opt == "0":
            print("Saliendo del sistema...")
            save_data(data)
            print("Datos guardados. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
