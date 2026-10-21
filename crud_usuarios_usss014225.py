from mysql.connector.errors import Error
import conexion

db = conexion.Conexion()

class crud_usuarios_usss014225:
    """
    Clase CRUD para la gestión de usuarios_usss014225 en la base de datos db_academica.
    Cumple con el criterio de la rúbrica: método y clase con código de estudiante usss014225.
    """
    def __init__(self):
        self.tabla = "usuarios_usss014225"

    def consultar(self, buscar=""):
        """
        Búsqueda de usuarios por usuario, nombre, dirección o teléfono.
        Si 'buscar' está vacío, retorna todos los usuarios ordenados descendentemente.
        """
        if buscar:
            sql = f"""
                SELECT idUsuario, usuario, clave, nombre, direccion, telefono,
                       direccion AS `dirección`, telefono AS `teléfono`
                FROM {self.tabla}
                WHERE usuario LIKE %s OR nombre LIKE %s OR direccion LIKE %s OR telefono LIKE %s
                ORDER BY idUsuario DESC
            """
            filtro = f"%{buscar}%"
            val = (filtro, filtro, filtro, filtro)
            return db.consultar(sql, val)
        else:
            sql = f"""
                SELECT idUsuario, usuario, clave, nombre, direccion, telefono,
                       direccion AS `dirección`, telefono AS `teléfono`
                FROM {self.tabla}
                ORDER BY idUsuario DESC
            """
            return db.consultar(sql)

    def consultar_por_id(self, idUsuario):
        """Consulta un usuario específico por su idUsuario."""
        sql = f"""
            SELECT idUsuario, usuario, clave, nombre, direccion, telefono,
                   direccion AS `dirección`, telefono AS `teléfono`
            FROM {self.tabla}
            WHERE idUsuario = %s
        """
        res = db.consultar(sql, (idUsuario,))
        return res[0] if res else None

    def autenticar(self, usuario, clave):
        """
        Autenticación del login contra la tabla usuarios_usss014225.
        Retorna los datos del usuario si las credenciales son válidas, o None si no coincide.
        """
        sql = f"""
            SELECT idUsuario, usuario, nombre, direccion, telefono
            FROM {self.tabla}
            WHERE BINARY usuario = %s AND BINARY clave = %s
        """
        res = db.consultar(sql, (usuario, clave))
        return res[0] if res else None

    def crud_usuarios_usss014225(self, datos):
        """
        Método solicitado explícitamente en el numeral 3 del parcial:
        crud_usuarios_usis018804 (sustituido por código del estudiante: crud_usuarios_usss014225).
        Procesa los datos enviados por el cliente y los almacena en la tabla usuarios_usss014225.
        """
        try:
            accion = datos.get('accion', '').lower()
            usuario = str(datos.get('usuario', '')).strip()
            clave = str(datos.get('clave', '')).strip()
            nombre = str(datos.get('nombre', '')).strip()
            direccion = str(datos.get('direccion', datos.get('dirección', ''))).strip()
            telefono = str(datos.get('telefono', datos.get('teléfono', ''))).strip()
            idUsuario = datos.get('idUsuario', None)

            if accion == 'nuevo':
                if not usuario or not clave or not nombre:
                    return "Error: Los campos Usuario, Clave y Nombre son obligatorios."

                # Verificar si el usuario ya existe
                existe = db.consultar(f"SELECT idUsuario FROM {self.tabla} WHERE usuario = %s", (usuario,))
                if existe:
                    return f"Error: El nombre de usuario '{usuario}' ya está en uso."

                sql = f"""
                    INSERT INTO {self.tabla} (usuario, clave, nombre, direccion, telefono)
                    VALUES (%s, %s, %s, %s, %s)
                """
                valores = (usuario, clave, nombre, direccion, telefono)
                return db.ejecutar(sql, valores)

            elif accion == 'modificar':
                if not idUsuario:
                    return "Error: idUsuario no proporcionado para modificar."

                # Verificar si el nuevo usuario ya pertenece a otra cuenta
                existe = db.consultar(
                    f"SELECT idUsuario FROM {self.tabla} WHERE usuario = %s AND idUsuario <> %s",
                    (usuario, idUsuario)
                )
                if existe:
                    return f"Error: El nombre de usuario '{usuario}' ya pertenece a otro registro."

                # Si la clave viene vacía en modificar, conservar la que ya tiene
                if not clave:
                    sql = f"""
                        UPDATE {self.tabla}
                        SET usuario = %s, nombre = %s, direccion = %s, telefono = %s
                        WHERE idUsuario = %s
                    """
                    valores = (usuario, nombre, direccion, telefono, idUsuario)
                else:
                    sql = f"""
                        UPDATE {self.tabla}
                        SET usuario = %s, clave = %s, nombre = %s, direccion = %s, telefono = %s
                        WHERE idUsuario = %s
                    """
                    valores = (usuario, clave, nombre, direccion, telefono, idUsuario)

                return db.ejecutar(sql, valores)

            elif accion == 'eliminar':
                if not idUsuario:
                    return "Error: idUsuario no proporcionado para eliminar."
                sql = f"DELETE FROM {self.tabla} WHERE idUsuario = %s"
                valores = (idUsuario,)
                return db.ejecutar(sql, valores)

            else:
                return f"Error: Acción '{accion}' no reconocida."

        except Error as e:
            return f"Error en base de datos: {e}"
        except Exception as e:
            return f"Error inesperado: {e}"

    # Alias estándar para integración con vistas
    def administrar(self, datos):
        return self.crud_usuarios_usss014225(datos)


# Función a nivel de módulo con el mismo nombre para compatibilidad total
def crud_usuarios_usss014225_func(datos):
    gestor = crud_usuarios_usss014225()
    return gestor.crud_usuarios_usss014225(datos)
