from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib import parse
from urllib.parse import urlparse, parse_qs
import crud_usuarios_usss014225
import json
import os

port = 3000
crudUsuarios = crud_usuarios_usss014225.crud_usuarios_usss014225()

class miServidor(SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            longitud = int(self.headers.get('Content-Length', 0))
            datos_raw = self.rfile.read(longitud).decode("utf-8")
            datos_raw = parse.unquote(datos_raw)
            datos = json.loads(datos_raw) if datos_raw else {}

            urlParse = urlparse(self.path)
            modulo = datos.get("modulo", "")
            accion = datos.get("accion", "")

            # ----------------------------------------------------
            # Autenticación / Login (Requerimiento 5 y Rúbrica)
            # ----------------------------------------------------
            if modulo == "login" or urlParse.path == "/login" or accion == "login":
                usr = datos.get("usuario", "").strip()
                pwd = datos.get("clave", "").strip()

                if not usr or not pwd:
                    respuesta = {"msg": "Error: Debe ingresar usuario y clave."}
                else:
                    usuario_db = crudUsuarios.autenticar(usr, pwd)
                    if usuario_db:
                        respuesta = {
                            "msg": "ok",
                            "usuario": {
                                "idUsuario": usuario_db["idUsuario"],
                                "usuario": usuario_db["usuario"],
                                "nombre": usuario_db["nombre"],
                                "direccion": usuario_db.get("direccion", ""),
                                "telefono": usuario_db.get("telefono", "")
                            }
                        }
                    else:
                        respuesta = {"msg": "Acceso denegado: Usuario o clave incorrectos."}

            # ----------------------------------------------------
            # CRUD de Usuarios (Requerimientos 2, 3, 4 y Rúbrica)
            # ----------------------------------------------------
            elif modulo in ["usuario", "usuarios"] or urlParse.path in ["/usuario", "/usuarios"]:
                resultado = crudUsuarios.crud_usuarios_usss014225(datos)
                respuesta = {"msg": resultado}

            else:
                respuesta = {"msg": "Módulo o acción no soportada."}

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta, ensure_ascii=False).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            error_resp = {"msg": f"Error interno en el servidor: {str(e)}"}
            self.wfile.write(json.dumps(error_resp, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)

        # Endpoint para consultar/buscar usuarios
        if urlParse.path in ["/usuarios", "/usuario"]:
            buscar = qs.get('buscar', [''])[0]
            datos = crudUsuarios.consultar(buscar)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(datos, ensure_ascii=False).encode("utf-8"))

        # Carga dinámica de vistas modulares HTML
        elif urlParse.path == "/vistas":
            nombre_form = qs.get('form', [''])[0]
            ruta_vista = os.path.join("modulos", f"{nombre_form}.html")
            if os.path.exists(ruta_vista):
                self.path = f"/modulos/{nombre_form}.html"
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"<h3>Vista '{nombre_form}' no encontrada.</h3>".encode("utf-8"))
                return
            return SimpleHTTPRequestHandler.do_GET(self)

        # Ruta raíz
        elif self.path in ["/", ""]:
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        # Archivos estáticos generales
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    print(f"======================================================")
    print(f" Servidor iniciado en http://localhost:{port}")
    print(f" Sistema Académico - Parcial II - USSS014225")
    print(f"======================================================")
    server = ThreadingHTTPServer(("localhost", port), miServidor)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
