from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

class TCGGamus:
    # Parámetros que permiten establecer la conexión con la base de datos MySQL
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = self.get_db_connection()
        self.cursor = self.conn.cursor()  # Cursor para ejecutar comandos SQL en la base de datos

        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)

    def get_db_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

# Crear una instancia
db_instance = TCGGamus(host='localhost', user='user', password='1234', database='tcg-gamus')

#Creación de rutas
# Listar
@app.route("/catalogo", methods=["GET"])
def listar_cartas():
    cursor = db_instance.get_db_connection().cursor()
    cursor.execute('SELECT * FROM producto') #Inserte nombre de la tabla que quiere listar y mostrar
    catalogo = cursor.fetchall()
    cursor.close()
    productos = catalogo.listar_cartas()
    return jsonify(productos)


# @app.route('/user/<card>')
# def show_card_gamu(card):
#     return f'User {card}'

if __name__ == "__main__":
    app.run(debug=True)
