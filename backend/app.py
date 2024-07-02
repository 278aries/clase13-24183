from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mysql.connector

import os
import time

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

class TCGGamus:

    #Establecer la conexión a la base de datos
    def get_db_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    # Constructor de la clase y parámetros que permiten establecer la conexión con la base de datos MySQL

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = self.get_db_connection()
        self.cursor = self.conn.cursor()  # Cursor para ejecutar comandos SQL en la base de datos

        #Verificar si existe la base de datos MySQL
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos:
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
        
        #CREAR TABLAS SI NO EXISTEN...
        # Crear tabla cartas si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cartas (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT NOT NULL,
            franquicia VARCHAR(50) NOT NULL,
            anio YEAR NOT NULL,
            estado ENUM('nueva', 'usada') NOT NULL DEFAULT 'nueva',
            precio DECIMAL(10,2) NOT NULL,
            imagen VARCHAR(255))''') 
        
        #Crear tabla carrito (detalle_pedido) si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS carrito (
            id_detalle_pedido INT PRIMARY KEY AUTO_INCREMENT,
            id_pedido INT NOT NULL,
            id_carta INT NOT NULL,
            cantidad INT NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
            FOREIGN KEY (id_carta) REFERENCES cartas(id_carta)''')
        
        #Crear tabla pedido si no existe
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS pedido (
            id_pedido INT PRIMARY KEY AUTO_INCREMENT,
            id_usuario INT NOT NULL,
            fecha_pedido DATE NOT NULL,
            estado_pedido ENUM('pendiente', 'pagado', 'enviado', 'entregado') NOT NULL DEFAULT 'pendiente',
            total DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario))''')

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

# Crear una instancia de la base de datos MySQL
tcggamus = TCGGamus(host='localhost', user='user', password='1234', database='tcg-gamus')

#Carpeta para guardar imágenes
ruta_destino = './static/imagenes/'

#MÉTODOS para manejar el catálogo  --------------------------------------------------------------------------------------------------------------------------------------
#Puede ver y guiarse con uno ya armado por la profe Nicole en drive de ejemplo

#CREAR/AGREGAR (Create)
def agregar_carta(self, nombre, descripcion, franquicia, anio, estado, precio, imagen):
 
 sql_agregar = '''INSERT INTO cartas (nombre, descripcion, franquicia, anio, estado, precio, imagen) 
 VALUES (%s, %s, %s, %s, %s, %s, %s, %s) '''
 valores = (nombre, descripcion, franquicia, anio, estado, precio, imagen)
 
 self.cursor.execute(sql_agregar, valores)
 self.conn.commit()
 return self.cursor.lastrowid

#MOSTRAR/LISTAR (Read / Get all)
def listar_cartas(self):
    cartas = self.cursor.execute("SELECT * FROM cartas")
    return cartas

#MOSTRAR/LISTAR (Read / Get one by id)
def consultar_carta(self, id):
    # Consultamos un producto a partir de su código
    self.cursor.execute(f"SELECT * FROM cartas WHERE id = {id}")
    cartaporuno = self.cursor.fetchone()
    return cartaporuno

#ACTUALIZAR (Update)
def actualizar_carta(self, id, new_nombre, new_descripcion, new_franquicia, new_anio, new_estado, new_precio, new_imagen):
    sql_actualizar = ''' UPDATE cartas
    SET nombre = %s,
       descripcion = %s,
       franquicia = %s,
       anio = %s,
       estado = %s,
       precio = %s,
       imagen = %s WHERE id = %s'''
    valores = (new_nombre, new_descripcion, new_franquicia, new_anio, new_estado, new_precio, new_imagen, id)

    self.cursor.execute(sql_actualizar, valores)
    self.conn.commit()
    return self.cursor.rowcount > 0

#ELIMINAR (delete)
def eliminar_carta(self, id):
    self.cursor.execute(f"DELETE FROM cartas WHERE id = {id}")
    self.conn.commit()
    return self.cursor.rowcount > 0

#MÉTODOS para manejar el carrito de compras -------------------------------------------------------------------------------------------------------
#Pendiente a modificar los métodos de acuerdo a las consultas creadas como procedimientos en MySQL

#CREAR/AGREGAR (Create)

def agregar_carrito(self, id_carta, cantidad):
    self.cursor.execute('''INSERT INTO carrito (id_carta, cantidad) VALUES (%s, %s)''', (id_carta, cantidad))
    self.conn.commit()
    return self.cursor.lastrowid

#MOSTRAR (Read / Get)
def mostrar_carrito(self):
    self.cursor.execute(
        '''SELECT c.id_detalle_pedido, c.id_carta, c.cantidad, c.precio_unitario,
        (c.cantidad * c.precio_unitario) AS total, ca.nombre, ca.descripcion
        FROM carrito c
        JOIN cartas ca ON c.id_carta = ca.id''') #Revisar bien MySQL
    return self.cursor.fetchall()

#ACTUALIZAR (Update)
def actualizar_carrito(self, id, cantidad):
    self.cursor.execute('''UPDATE carrito SET cantidad = %s WHERE id_carrito = %s''', (cantidad, id))
    self.conn.commit()
    return self.cursor.rowcount > 0

#ELIMINAR (delete)

def eliminar_carrito(self, id):
    self.cursor.execute(f"DELETE FROM carrito WHERE id = {id}")
    self.conn.commit()
    return self.cursor.rowcount > 0

# MOSTRAR - Mostramos los datos de un producto a partir de su código (DE PRUEBA Y PARA VISUALIZAR LOS DATOS)

def mostrar_carta(self, id):
    carta = self.consultar_carta(id)
    if carta:
            print("-" * 40)
            print(f"ID.....: {carta['id_carta']}")
            print(f"Descripción: {carta['descripcion']}")
            print(f"Franquicia...: {carta['franquicia']}")
            print(f"Año..: {carta['anio']}")
            print(f"Estado..: {carta['estado']}")
            print(f"Precio.....: {carta['precio']}")
            print(f"Imagen.....: {carta['imagen']}")
            print("-" * 40)
    else:
        print("Carta no encontrada.")

#Creación de rutas con Flask -------------------------------------------------------------------------------------------------------------------------------------
# Crear una instancia de la clase Catalogo (Alguien puede completar y agregar lo de esta parte junto con lo de pythonwhere)
# ?????????


# CARTAS ---------------------------------------------------------------------------------------------------------------------------------------------

# LISTAR/MOSTRAR (Get all)
@app.route("/catalogo", methods=["GET"])
def listar_cartas():
    #El método devuelve una lista con todos los productos en formato JSON.
    productos = tcggamus.listar_cartas()
    return jsonify(productos)

# MOSTRAR POR ID (Get id)
@app.route("/catalogo/<int:id>", methods=["GET"])
def mostrar_cartas(id):
    carta = tcggamus.consultar_carta(id)
    if carta:
        return jsonify(carta), 101
    else:
        return "Producto no encontrado", 404

#AGREGAR (Post)
@app.route("/catalogo", methods=["POST"])
def agregar_carta():  # Recojo los datos del form
    descripcion = request.form['descripcion']
    franquicia = request.form['franquicia']
    anio = request.form['anio']
    estado = request.form['estado']
    precio = request.form['precio'] 
    imagen = request.files['imagen']
    nombre_imagen = ""

 # Procesamiento de la imagen
    imagen = request.files['imagen']
    nombre_imagen = secure_filename(imagen.filename)
    nombre_base, extension = os.path.splitext(nombre_imagen)
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"

 #Crear el nuevo producto
    nuevo_id = tcggamus.agregar_item(descripcion, franquicia, anio, estado, precio, nombre_imagen)
    if nuevo_id: 
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
        print("¡La imagen se guardó correctamente!")
        return jsonify({"mensaje": "Producto de carta agregado correctamente.", "id": nuevo_id, "imagen": nombre_imagen}), 201
    
    else:
        return jsonify({"mensaje": "Error al agregar el producto."}), 500


#MODIFICAR (Update)
@app.route("/cartas/<int:id>", methods=["PUT"])
def actualizar_carta(id):
    # Recojo los datos del form
    nueva_descripcion = request.form.get("descripcion")
    nueva_franquicia = request.form.get("franquicia")
    nuevo_anio = request.form.get("anio")
    nuevo_estado = request.form.get("estado")
    nuevo_precio = request.form.get("precio")

    #Verificar si se proporciona una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']

        nombre_imagen = secure_filename(imagen.filename)
        nombre_base, extension = os.path.splitext(nombre_imagen)
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}"
        imagen.save(os.path.join(ruta_destino, nombre_imagen))
    
        #Busco si existe la imagen vieja guardada 
        carta = tcggamus.consultar_carta(id)
        if carta:
            imagen_vieja = carta["imagen"]
            ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:
        carta =tcggamus.consultar_carta(id) #si no se proporciona la nueva imagen, usa la imagen existente
        if carta:
            nombre_imagen = carta["imagen"]

    # Actualización del producto
    if tcggamus.actualizar_carta(id, nueva_descripcion, nueva_franquicia, nuevo_anio, nuevo_estado, nuevo_precio, nombre_imagen):
        return jsonify({"mensaje": "Producto de carta modificado"}), 200
    else:
        return jsonify({"mensaje": "Producto de carta no encontrado"}), 404

#ELIMINAR (Delete)
@app.route("/cartas/<int:id>", methods=["DELETE"])
def eliminar_carta():
    carta = tcggamus.consultar_carta(id)
    if carta:
        imagen_vieja = carta["imagen"]
        ruta_imagen = os.path.join(ruta_destino, imagen_vieja)

        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
            
        if carta.eliminar_carta(id):
             return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 404

#CARRITO -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#LISTAR/MOSTRAR (Get all)
@app.route("/carrito", methods=["GET"])
def listar_carrito():
    #El método devuelve una lista con todos los productos en formato JSON.
    items = tcggamus.mostrar_carrito()
    return jsonify(items)

#MODIFICAR (Update)
@app.route("/carrito/<int:id_detalle_pedido>", methods=["PUT"])
def actualizar_carrito(id_detalle_pedido):
    cantidad = request.form.get("cantidad")
    exito = tcggamus.actualizar_carrito(id_detalle_pedido, cantidad)
    if exito:
        return jsonify({"mensaje": "Cantidad actualizada correctamente en el item."}), 200
    else:
        return jsonify({"mensaje": "Error al actualizar la cantidad en el item."}), 500

#ELIMINAR (Delete)
@app.route("/carrito/<int:id_detalle_pedido>", methods= ["DELETE"])
def eliminar_carrito(id_detalle_pedido):
    eliminar = tcggamus.eliminar_carrito(id_detalle_pedido)
    if eliminar:
        return jsonify({"mensaje": "Carta eliminada del carrito correctamente."}), 200
    else:
        return jsonify({"mensaje": "Error al eliminar la carta del carrito."}), 500

if __name__ == "__main__":
    app.run(debug=True)