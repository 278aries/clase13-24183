# app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
# Instalar con pip install Flask
from flask import Flask, request, jsonify #, render_template
# Instalar con pip install flask-cors
from flask_cors import CORS
# Instalar con pip install mysql-connector-python
import mysql.connector
# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename
import os
import time
#--------------------------------------------------------------------
app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas
#--------------------------------------------------------------------
class Catalogo:         # Constructor de la clase
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            #connection_timeout=288000
            #con.ping(True)
        )
        self.cursor = self.conn.cursor()
        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            apellidos VARCHAR(255) NOT NULL,
            direccion VARCHAR(255))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
            codigo INT AUTO_INCREMENT PRIMARY KEY,
            descripcion VARCHAR(255) NOT NULL,
            cantidad INT NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            imagen_url VARCHAR(255),
            proveedor INT(4))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cartas (
            id_carta INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR (250) NOT NULL,
            franquicia VARCHAR(50) NOT NULL,
            precio DECIMAL(10,2) NOT NULL,
            imagen_url VARCHAR(255))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS pedido (
            id_pedido INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            fecha_pedido DATE NOT NULL,
            estado_pedido ENUM('pendiente', 'pagado', 'enviado', 'entregado') NOT NULL DEFAULT 'pendiente',
            total DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS carrito (
            id_detalle_pedido INT AUTO_INCREMENT PRIMARY KEY,
            cantidad INT NOT NULL,
            id_pedido INT NOT NULL,
            id_carta INT NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido),
            FOREIGN KEY (id_carta) REFERENCES cartas(id_carta))''')
        self.conn.commit()
        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

#----------------------------------------------------------------------------------------------COMIENZO CARTAS
    def agregar_carta(self, nombre, descripcion, franquicia, precio, imagen):
        sql = """INSERT INTO cartas (nombre, descripcion, franquicia, precio, imagen_url)
          VALUES (%s, %s, %s, %s, %s)"""
        valores = (nombre, descripcion, franquicia, precio, imagen)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.lastrowid
    #-----------------------------------------------------------------------------------------CONSULTAR CARTAS
    def consultar_carta(self, id_carta):
        self.cursor.execute(f"SELECT * FROM cartas WHERE id_carta = {id_carta}")
        return self.cursor.fetchone() #Me da el diccionario o None si no existe
    #-----------------------------------------------------------------------------------------MODIFICAR CARTAS
    def modificar_carta(self, codigo, nuevo_nombre, nueva_descripcion, nueva_franquicia, nuevo_precio, nueva_imagen):
        sql = "UPDATE cartas SET nombre= %s, descripcion = %s, franquicia = %s, precio = %s, imagen_url= %s WHERE id_carta = %s"
        valores = (nuevo_nombre, nueva_descripcion, nueva_franquicia, nuevo_precio, nueva_imagen, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0
    #-------------------------------------------------------------------------------- LISTAR CARTAS
    def listar_cartas(self):
        self.cursor.execute("SELECT * FROM cartas")
        cartas = self.cursor.fetchall()
        return cartas
    #-------------------------------------------------------------------------------- ELIMINAR CARTAS
    def eliminar_carta(self, codigo):
        self.cursor.execute(f"DELETE FROM cartas WHERE id_carta = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0
    #-------------------------------------------------------------------------------- MOSTRAR CARTAS
    def mostrar_carta(self, id_carta):
        carta = self.consultar_carta(id_carta)
        if carta:
            print("-" * 40)
            print(f"Código.....: {carta['id_carta']}")
            print(f"Nombre.....: {carta['nombre']}")
            print(f"Descripción: {carta['descripcion']}")
            print(f"Franquicia.: {carta['franquicia']}")
            print(f"Precio.....: {carta['precio']}")
            print(f"Imagen.....: {carta['imagen_url']}")
            print("-" * 40)
        else:
            print("Carta no encontrada.")
#--------------------------------------------------------------------------------------FIN CARTAS

#--------------------------------------------------------------------------------------INICIO PRODUCTOS
    def agregar_producto(self, descripcion, cantidad, precio, imagen, proveedor):
        sql = """INSERT INTO productos (descripcion, cantidad, precio, imagen_url, proveedor)
          VALUES (%s, %s, %s, %s, %s)"""
        valores = (descripcion, cantidad, precio, imagen, proveedor)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.lastrowid
    #----------------------------------------------------------------
    def consultar_producto(self, codigo):
        self.cursor.execute(f"SELECT * FROM productos WHERE codigo = {codigo}")
        return self.cursor.fetchone() #Me da el diccionario o None si no existe
    #----------------------------------------------------------------
    def modificar_producto(self, codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor):
        sql = "UPDATE productos SET descripcion = %s, cantidad = %s, precio = %s, imagen_url = %s, proveedor = %s WHERE codigo = %s"
        valores = (nueva_descripcion, nueva_cantidad, nuevo_precio, nueva_imagen, nuevo_proveedor, codigo)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0
    #----------------------------------------------------------------
    def listar_productos(self):
        self.cursor.execute("SELECT * FROM productos")
        productos = self.cursor.fetchall()
        return productos
    #----------------------------------------------------------------
    def eliminar_producto(self, codigo):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM productos WHERE codigo = {codigo}")
        self.conn.commit()
        return self.cursor.rowcount > 0
    #----------------------------------------------------------------
    def mostrar_producto(self, codigo):
        # Mostramos los datos de un producto a partir de su código
        producto = self.consultar_producto(codigo)
        if producto:
            print("-" * 40)
            print(f"Código.....: {producto['codigo']}")
            print(f"Descripción: {producto['descripcion']}")
            print(f"Cantidad...: {producto['cantidad']}")
            print(f"Precio.....: {producto['precio']}")
            print(f"Imagen.....: {producto['imagen_url']}")
            print(f"Proveedor..: {producto['proveedor']}")
            print("-" * 40)
        else:
            print("Producto no encontrado.")
#-----------------------------------------------------------------------------------------FIN PRODUCTOS

#-----------------------------------------------------------------------------------------------------
#                                                                                       CUERPO DEL PROGRAMA
#-----------------------------------------------------------------------------------------------------
# Al Crear una instancia de la clase Catalogo aqui hace que la misma quede activa pero al pasar el tiempo mysql cierra la conexion por tiempo o inactividad,
# esto lo encontramos viendo los los logs del entorno mysql en el path del proyecto (/var/log/tcggamu.pythonanywhere.com.error.log)
# para resolverlo decidimos instanciar el catalogo en cada interaccion con la base de datos de esta forma no se debe estar reiniciando el servicio de pythonanywere...

#catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')

# Carpeta para guardar las imagenes.
RUTA_DESTINO = '/home/tcggamu/mysite/static/imagenes'


#-----------------------------------------------------------------------------------------INICIO CARTAS--------------------------------------------------------------------------
#--------------------------------------------------------------------
# Listar todos las cartas
#--------------------------------------------------------------------
@app.route("/cartas", methods=["GET"])
def listar_cartas():
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    cartas = catalogo.listar_cartas()
    return jsonify(cartas)
#--------------------------------------------------------------------
# Mostrar una sola carta según su código
#--------------------------------------------------------------------
@app.route("/cartas/<int:codigo>", methods=["GET"])
def mostrar_carta(codigo):
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    producto = catalogo.consultar_carta(codigo)
    if producto:
        return jsonify(producto), 201
    else:
        return "Carta no encontrada", 404

#--------------------------------------------------------------------
# Agregar un carta
#--------------------------------------------------------------------
@app.route("/cartas", methods=["POST"])
def agregar_carta():
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    #Recojo los datos del form
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    franquicia = request.form['franquicia']
    # anio = request.form['anio']
    precio = request.form['precio']
    imagen = request.files['imagen']
    nombre_imagen=""
    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    nuevo_codigo = catalogo.agregar_carta(nombre, descripcion, franquicia, precio, nombre_imagen)
    if nuevo_codigo:
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        print("Se guardo!")
        #Si el producto se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
        return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        #Si el producto no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
        return jsonify({"mensaje": "Error al agregar el producto."}), 500

#--------------------------------------------------------------------
# Modificar carta segun su  código
#--------------------------------------------------------------------
@app.route("/cartas/<int:codigo>", methods=["PUT"])
def modificar_carta(codigo):
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    #Se recuperan los nuevos datos del formulario
    nuevo_nombre = request.form.get("nombre")
    nueva_descripcion = request.form.get("descripcion")
    nueva_franquicia = request.form.get("franquicia")
    nuevo_precio = request.form.get("precio")
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.
        # Guardar la imagen en el servidor
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        # Busco el producto guardado
        carta = catalogo.consultar_carta(codigo)
        if carta: # Si existe el producto...
            imagen_vieja = carta["imagen_url"]
            if imagen_vieja:
                # Armo la ruta a la imagen
                ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
                # Y si existe la borro.
                if os.path.exists(ruta_imagen):
                    os.remove(ruta_imagen)
    else:
        # Si no se proporciona una nueva imagen, simplemente usa la imagen existente del producto
        carta = catalogo.consultar_carta(codigo)
        if carta:
            nombre_imagen = carta["imagen_url"]
    # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if catalogo.modificar_carta (codigo, nuevo_nombre, nueva_descripcion, nueva_franquicia, nuevo_precio, nombre_imagen):
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        #Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Producto no encontrado"}), 404

#--------------------------------------------------------------------
# Eliminar una carta según su código..
#--------------------------------------------------------------------
@app.route("/cartas/<int:codigo>", methods=["DELETE"])
def eliminar_carta(codigo):
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    # Busco el producto en la base de datos
    producto = catalogo.consultar_carta(codigo)
    if producto: # Si el producto existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = producto["imagen_url"]
        # Armo la ruta a la imagen
        if imagen_vieja:
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
            # Y si existe, la elimina del sistema de archivos.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_carta(codigo):
            #Si el producto se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Carta eliminada"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si el producto no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar la carta."}), 500
    else:
        #Si el producto no se encuentra (por ejemplo, si no existe un producto con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Carta no encontrada"}), 404

#--------------------------------------------------------------------------------------------------FIN CARTAS------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------
# Listar todos los productos
#--------------------------------------------------------------------
@app.route("/productos", methods=["GET"])
def listar_productos():
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    productos = catalogo.listar_productos()
    return jsonify(productos)
#--------------------------------------------------------------------
# Mostrar un sólo producto según su código
#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["GET"])
def mostrar_producto(codigo):
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    producto = catalogo.consultar_producto(codigo)
    if producto:
        return jsonify(producto), 201
    else:
        return "Producto no encontrado", 404
#--------------------------------------------------------------------
# Agregar un producto
#--------------------------------------------------------------------
@app.route("/productos", methods=["POST"])
def agregar_producto():
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    #Recojo los datos del form
    descripcion = request.form['descripcion']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    imagen = request.files['imagen']
    proveedor = request.form['proveedor']
    nombre_imagen=""
    # Genero el nombre de la imagen
    nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
    nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
    nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.

    nuevo_codigo = catalogo.agregar_producto(descripcion, cantidad, precio, nombre_imagen, proveedor)
    if nuevo_codigo:
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        print("Se guardo!")
        #Si el producto se agrega con éxito, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 201 (Creado).
        return jsonify({"mensaje": "Producto agregado correctamente.", "codigo": nuevo_codigo, "imagen": nombre_imagen}), 201
    else:
        #Si el producto no se puede agregar, se devuelve una respuesta JSON con un mensaje de error y un código de estado HTTP 500 (Internal Server Error).
        return jsonify({"mensaje": "Error al agregar el producto."}), 500
#--------------------------------------------------------------------
# Modificar un producto según su código
#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["PUT"])
#La ruta Flask /productos/<int:codigo> con el método HTTP PUT está diseñada para actualizar la información de un producto existente en la base de datos, identificado por su código.
#La función modificar_producto se asocia con esta URL y es invocada cuando se realiza una solicitud PUT a /productos/ seguido de un número (el código del producto).
def modificar_producto(codigo):
    # Crear una instancia de la clase Catalogo para generar la nueva conexion con el mysql... arreglo para que no haya que reiniciar el servicio de python Anywhere
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    #Se recuperan los nuevos datos del formulario
    nueva_descripcion = request.form.get("descripcion")
    nueva_cantidad = request.form.get("cantidad")
    nuevo_precio = request.form.get("precio")
    nuevo_proveedor = request.form.get("proveedor")
    # Verifica si se proporcionó una nueva imagen
    if 'imagen' in request.files:
        imagen = request.files['imagen']
        # Procesamiento de la imagen
        nombre_imagen = secure_filename(imagen.filename) #Chequea el nombre del archivo de la imagen, asegurándose de que sea seguro para guardar en el sistema de archivos
        nombre_base, extension = os.path.splitext(nombre_imagen) #Separa el nombre del archivo de su extensión.
        nombre_imagen = f"{nombre_base}_{int(time.time())}{extension}" #Genera un nuevo nombre para la imagen usando un timestamp, para evitar sobreescrituras y conflictos de nombres.
        # Guardar la imagen en el servidor
        imagen.save(os.path.join(RUTA_DESTINO, nombre_imagen))
        # Busco el producto guardado
        producto = catalogo.consultar_producto(codigo)
        if producto: # Si existe el producto...
            imagen_vieja = producto["imagen_url"]
            # Armo la ruta a la imagen
            ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
            # Y si existe la borro.
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
    else:
        # Si no se proporciona una nueva imagen, simplemente usa la imagen existente del producto
        producto = catalogo.consultar_producto(codigo)
        if producto:
            nombre_imagen = producto["imagen_url"]
    # Se llama al método modificar_producto pasando el codigo del producto y los nuevos datos.
    if catalogo.modificar_producto(codigo, nueva_descripcion, nueva_cantidad, nuevo_precio, nombre_imagen, nuevo_proveedor):
        #Si la actualización es exitosa, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
        return jsonify({"mensaje": "Producto modificado"}), 200
    else:
        #Si el producto no se encuentra (por ejemplo, si no hay ningún producto con el código dado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Producto no encontrado"}), 404

#--------------------------------------------------------------------
# Eliminar un producto según su código
#--------------------------------------------------------------------
@app.route("/productos/<int:codigo>", methods=["DELETE"])
#La ruta Flask /productos/<int:codigo> con el método HTTP DELETE está diseñada para eliminar un producto específico de la base de datos, utilizando su código como identificador.
#La función eliminar_producto se asocia con esta URL y es llamada cuando se realiza una solicitud DELETE a /productos/ seguido de un número (el código del producto).
def eliminar_producto(codigo):
    catalogo = Catalogo(host='tcggamu.mysql.pythonanywhere-services.com', user='tcggamu', password='Clave123', database='tcggamu$default')
    # Busco el producto en la base de datos
    producto = catalogo.consultar_producto(codigo)
    if producto: # Si el producto existe, verifica si hay una imagen asociada en el servidor.
        imagen_vieja = producto["imagen_url"]
        # Armo la ruta a la imagen
        ruta_imagen = os.path.join(RUTA_DESTINO, imagen_vieja)
        # Y si existe, la elimina del sistema de archivos.
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        # Luego, elimina el producto del catálogo
        if catalogo.eliminar_producto(codigo):
            #Si el producto se elimina correctamente, se devuelve una respuesta JSON con un mensaje de éxito y un código de estado HTTP 200 (OK).
            return jsonify({"mensaje": "Producto eliminado"}), 200
        else:
            #Si ocurre un error durante la eliminación (por ejemplo, si el producto no se puede eliminar de la base de datos por alguna razón), se devuelve un mensaje de error con un código de estado HTTP 500 (Error Interno del Servidor).
            return jsonify({"mensaje": "Error al eliminar el producto"}), 500
    else:
        #Si el producto no se encuentra (por ejemplo, si no existe un producto con el codigo proporcionado), se devuelve un mensaje de error con un código de estado HTTP 404 (No Encontrado).
        return jsonify({"mensaje": "Producto no encontrado"}), 404
#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)