import mysql.connector
from mysql.connector import Error
import threading

class Conexion:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 3307
        self.user = "root"
        self.password = ""
        self.database = "db_sistema_impuestos"
        self.conexion = None
        self.lock = threading.RLock()
        self.conectar()

    def conectar(self):
        with self.lock:
            # Intentar conectar al puerto 3307 (XAMPP configurado) o fallback al 3306
            puertos = [self.port, 3306]
            for p in puertos:
                try:
                    self.conexion = mysql.connector.connect(
                        host=self.host,
                        port=p,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        use_pure=True
                    )
                    if self.conexion.is_connected():
                        self.port = p
                        return True
                except Exception as e:
                    pass
            print("No se pudo conectar a la base de datos MySQL en puertos 3307 ni 3306")
            return False

    def verificar_conexion(self):
        with self.lock:
            try:
                if self.conexion is None or not self.conexion.is_connected():
                    self.conectar()
            except Exception:
                self.conectar()

    def consultar(self, sql, valores=None):
        with self.lock:
            try:
                self.verificar_conexion()
                cursor = self.conexion.cursor(dictionary=True)
                if valores:
                    cursor.execute(sql, valores)
                else:
                    cursor.execute(sql)
                resultados = cursor.fetchall()
                cursor.close()
                return resultados
            except Error as e:
                print(f"Error al consultar la base de datos: {e}")
                return None

    def ejecutar(self, sql, datos=None):
        with self.lock:
            try:
                self.verificar_conexion()
                cursor = self.conexion.cursor()
                if datos:
                    cursor.execute(sql, datos)
                else:
                    cursor.execute(sql)
                self.conexion.commit()
                ultimo_id = cursor.lastrowid
                cursor.close()
                return 'ok'
            except Error as e:
                print(f"Error al ejecutar la consulta: {e}")
                return f'Error: {e}'